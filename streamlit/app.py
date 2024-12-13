import streamlit as st
import pandas as pd
import sys
import numpy as np
sys.path.append('../notebooks/utils')
from recommender import AmazonRecommender 

# Configuration de la page
st.set_page_config(
    page_title="Amazon Product Recommender",
    page_icon="🛍️",
    layout="wide"
)

# Titre de l'application
st.title("🛍️ Système de Recommandation Amazon")

def calculate_search_relevance(row, search_terms, exact_phrase):
    """
    Calcule un score de pertinence avec une forte priorisation des Echo Dot
    """
    title = str(row['title']).lower()
    category = str(row['categoryName']).lower()
    score = 0
    
    # Priorisation maximale pour Echo Dot
    if "echo dot" in title:
        score += 100  # Score de base très élevé pour Echo Dot
        # Bonus supplémentaire si c'est au début du titre
        if title.startswith("echo dot"):
            score += 50
        
        # Bonus pour les générations plus récentes
        if any(f"{n}th generation" in title for n in ['5', '4', '3']):
            score += 30
            
    # Forte pénalité pour les accessoires
    accessory_keywords = [
        'cable', 'case', 'cover', 'accessory', 'accessories', 'stand', 
        'mount', 'holder', 'protector', 'aux', 'adapter'
    ]
    if any(word in title.lower() for word in accessory_keywords):
        score -= 200  # Pénalité très forte pour les accessoires
        
    # Bonus catégorie
    if category == 'smart speakers':
        score += 40
    elif category == 'hi-fi speakers':
        score += 20
        
    # Bonus qualité produit (plus faible impact)
    score += min(row['stars'], 5)  # Max 5 points pour les étoiles
    score += min(np.log1p(row['reviews']) / 20, 2.5)  # Max 2.5 points pour les avis
    
    return max(score, 0)



@st.cache_data
def load_data():
    """
    Charge et prépare les données pour l'application
    """
    try:
        df = pd.read_csv("../data/clean/amazon_uk_final.csv")
        
        required_columns = ['title', 'price', 'stars', 'reviews', 'categoryName', 'imgUrl', 'productURL']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Colonnes manquantes: {missing_columns}")
        
        df = df.dropna(subset=['title', 'price', 'stars', 'reviews', 'categoryName'])
        df = df[df['price'] > 0]
        
        return df
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return None

# Chargement des données
df = load_data()

if df is not None:
    try:
        recommender = AmazonRecommender()
        recommender.fit(df)
        st.success("Données chargées avec succès!")
        
        st.sidebar.write(f"Total produits: {len(df):,}")
        
        # Recherche produit améliorée
        search_query = st.text_input("🔍 Rechercher un produit", "")
        
        filtered_df = df.copy()
        
        # Dans la partie recherche de l'application
        if search_query:
            search_terms = search_query.lower().split()
            exact_phrase = search_query.lower()
            
            # Recherche initiale plus stricte
            if 'echo dot' in exact_phrase:
                # Recherche spécifique pour Echo Dot
                mask = (
                    filtered_df['title'].str.lower().str.contains('echo dot', na=False) |
                    (filtered_df['categoryName'] == 'Smart Speakers')
                )
            else:
                # Recherche générale pour les autres termes
                mask = filtered_df['title'].str.lower().str.contains('|'.join(search_terms), na=False)
            
            filtered_df = filtered_df[mask]
            
            if len(filtered_df) > 0:
                filtered_df['search_relevance'] = filtered_df.apply(
                    lambda x: calculate_search_relevance(x, search_terms, exact_phrase),
                    axis=1
                )
                
                # Filtrer les scores très bas
                filtered_df = filtered_df[filtered_df['search_relevance'] > 0]
                filtered_df = filtered_df.sort_values('search_relevance', ascending=False)
                
                # Affichage du score pour le debug (à enlever plus tard)
                filtered_df['debug_score'] = filtered_df['search_relevance']
                
                st.write(f"Résultats pour '{search_query}': {len(filtered_df)} produits")
        
        # Suite du code existant pour les filtres
        categories = ["Toutes les catégories"] + sorted(df['categoryName'].unique().tolist())
        selected_category = st.sidebar.selectbox(
            "Sélectionnez une catégorie",
            categories
        )
        
        if selected_category != "Toutes les catégories":
            filtered_df = filtered_df[filtered_df['categoryName'] == selected_category]
        
        
        # Filtre par prix
        price_min = float(filtered_df['price'].min())
        price_max = float(filtered_df['price'].max())
        price_range = st.sidebar.slider(
            "Gamme de prix (£)",
            min_value=price_min,
            max_value=price_max,
            value=(price_min, min(price_max, 100.0))
        )
        
        filtered_df = filtered_df[
            (filtered_df['price'] >= price_range[0]) &
            (filtered_df['price'] <= price_range[1])
        ]
        
        # Filtre par note
        min_rating = st.sidebar.slider(
            "Note minimale",
            1.0, 5.0, 4.0, 0.5
        )
        
        # Filtre par nombre d'avis
        min_reviews = st.sidebar.number_input(
            "Nombre minimum d'avis",
            0,
            int(filtered_df['reviews'].max()),
            100
        )
        
        filtered_df = filtered_df[
            (filtered_df['stars'] >= min_rating) &
            (filtered_df['reviews'] >= min_reviews)
        ]
        
        # Statistiques de filtrage
        st.sidebar.write("Statistiques de filtrage:")
        st.sidebar.write(f"Produits affichés: {len(filtered_df):,}")
        
        # Tri des résultats
        sort_options = {
            "Les plus pertinents": "popularity_score",  # Utiliser directement la colonne du score de popularité
            "Prix croissant": "price",
            "Prix décroissant": "price",
            "Meilleures notes": "stars",
            "Plus d'avis": "reviews"
        }

        sort_by = st.selectbox("Trier par", list(sort_options.keys()))

        # Application du tri de manière plus sûre
        try:
            if sort_by == "Prix décroissant":
                filtered_df = filtered_df.sort_values(by=sort_options[sort_by], ascending=False)
            elif sort_by == "Les plus pertinents":
                # Calcul d'un score de pertinence sécurisé
                filtered_df['relevance_score'] = filtered_df['stars'] * np.log1p(filtered_df['reviews'])
                filtered_df = filtered_df.sort_values(by='relevance_score', ascending=False)
            else:
                filtered_df = filtered_df.sort_values(by=sort_options[sort_by], ascending=True)
        except Exception as e:
            st.error(f"Erreur lors du tri: {str(e)}")
            # Continuer sans tri si une erreur se produit
        
        # Affichage des produits
        if len(filtered_df) > 0:
            st.write(f"Affichage des produits ({len(filtered_df)} résultats):")
            
            # Limitation à 30 produits
            filtered_df = filtered_df.head(30)
            
            # Affichage en grille
            cols = st.columns(3)
            for idx, product in filtered_df.iterrows():
                col_idx = idx % 3
                with cols[col_idx]:
                    st.markdown("---")
                    if pd.notna(product['imgUrl']):
                        st.image(product['imgUrl'], width=200)
                    st.markdown(f"**{product['title'][:100]}...**")
                    st.write(f"💰 Prix: £{product['price']:.2f}")
                    st.write(f"⭐ Note: {product['stars']:.1f}/5 ({int(product['reviews']):,} avis)")
                    st.write(f"📁 {product['categoryName']}")
                    
                    if pd.notna(product['productURL']):
                        st.markdown(f"[Voir sur Amazon]({product['productURL']})")
                    
                    if st.button(f"📊 Voir recommandations", key=f"btn_{idx}"):
                        try:
                            recommendations = recommender.get_similar_products(idx)
                            if not recommendations.empty:
                                st.subheader("Recommandations similaires")
                                for _, rec in recommendations.iterrows():
                                    st.markdown("---")
                                    # Gestion sécurisée de l'affichage de l'image
                                    if 'imgUrl' in rec and pd.notna(rec['imgUrl']):
                                        try:
                                            st.image(rec['imgUrl'], width=150)
                                        except:
                                            st.write("🖼️ Image non disponible")
                                    
                                    # Affichage sécurisé des autres informations
                                    st.markdown(f"**{rec.get('title', 'Titre non disponible')[:100]}...**")
                                    st.write(f"💰 Prix: £{rec.get('price', 0):.2f}")
                                    st.write(f"⭐ Note: {rec.get('stars', 0):.1f}/5 ({int(rec.get('reviews', 0)):,} avis)")
                                    st.write(f"📁 {rec.get('categoryName', 'Catégorie non disponible')}")
                                    
                                    if 'productURL' in rec and pd.notna(rec['productURL']):
                                        st.markdown(f"[Voir sur Amazon]({rec['productURL']})")
                            else:
                                st.warning("Aucune recommandation trouvée.")
                        except Exception as e:
                            st.error(f"Erreur lors de l'affichage des recommandations: {str(e)}")
        else:
            st.warning("Aucun produit ne correspond aux critères sélectionnés.")
        
    except Exception as e:
        st.error(f"Une erreur s'est produite: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Développé avec ❤️ par [Votre nom]")