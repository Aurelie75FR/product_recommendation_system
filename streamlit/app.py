import streamlit as st
import pandas as pd
import sys
import numpy as np
# sys.path.append('../notebooks/utils') # didn't works anymore and don't know why
from recommender_sys import AmazonRecommender

# Page config
st.set_page_config(
    page_title="Amazon Product Recommender",
    page_icon="🛍️",
    layout="wide"
)

# Init sessions
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

def calculate_search_relevance(row, search_terms, exact_phrase): # update this func for all kw
    """
    Calcule un score de pertinence avec une forte priorisation des Echo Dot
    """
    title = str(row['title']).lower()
    category = str(row['categoryName']).lower()
    score = 0
    
    if "echo dot" in title:
        score += 100
        if title.startswith("echo dot"):
            score += 50
        if any(f"{n}th generation" in title for n in ['5', '4', '3']):
            score += 30
            
    accessory_keywords = [
        'cable', 'case', 'cover', 'accessory', 'accessories', 'stand', 
        'mount', 'holder', 'protector', 'aux', 'adapter'
    ]
    if any(word in title.lower() for word in accessory_keywords):
        score -= 200
        
    if category == 'smart speakers':
        score += 40
    elif category == 'hi-fi speakers':
        score += 20
        
    score += min(row['stars'], 5)
    score += min(np.log1p(row['reviews']) / 20, 2.5)
    
    return max(score, 0)

def show_product_detail(product, df):
    """
    render product page details
    """
    # Back btn
    if st.button("← Retour aux résultats"):
        st.session_state.current_page = 'main'
        st.rerun()

    # Select product details
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if pd.notna(product.get('imgUrl')):
            try:
                st.image(product['imgUrl'], width=300)
            except:
                st.write("🖼️ Image non disponible")
            
    with col2:
        st.title(product['title'])
        st.write(f"💰 Prix: £{product['price']:.2f}")
        st.write(f"⭐ Note: {product['stars']:.1f}/5 ({int(product['reviews']):,} avis)")
        st.write(f"📁 Catégorie: {product['categoryName']}")
        
        if pd.notna(product.get('productURL')):
            st.markdown(f"[Voir sur Amazon]({product['productURL']})")

    # Recommendations section
    st.markdown("---")
    st.header("Produits similaires recommandés")
    
    try:
        # Init recommender
        recommender = AmazonRecommender()
        recommender.fit(df)
        
        # Get recommendations
        recommendations = recommender.get_similar_products(product.name)
        
        if not recommendations.empty:
            # Affichage en grille des recommandations
            cols = st.columns(3)
            for idx, rec in recommendations.iterrows():
                with cols[idx % 3]:
                    # Image du produit
                    if pd.notna(rec.get('imgUrl')):
                        try:
                            st.image(rec['imgUrl'], width=200)
                        except:
                            st.write("🖼️ Image non disponible")
                    
                    # Informations du produit
                    st.markdown(f"**{rec['title'][:100]}...**")
                    st.write(f"💰 Prix: £{rec['price']:.2f}")
                    st.write(f"⭐ Note: {rec['stars']:.1f}/5 ({int(rec['reviews']):,} avis)")
                    st.write(f"📁 {rec['categoryName']}")
                    
                    # Liens et actions
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if pd.notna(rec.get('productURL')):
                            st.markdown(f"[Voir sur Amazon]({rec['productURL']})")
                    with col2:
                        if st.button("Voir détails", key=f"rec_{idx}"):
                            st.session_state.selected_product = rec
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.warning("Aucune recommandation trouvée pour ce produit.")
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des recommandations: {str(e)}")

# def show_product_detail(product, df):
#     """
#     Affiche la page détaillée d'un produit
#     """
#     if st.button("← Retour aux résultats"):
#         st.session_state.current_page = 'main'
#         st.rerun()
    
#     # Affichage du produit principal
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         if pd.notna(product.get('imgUrl')):
#             try:
#                 st.image(product['imgUrl'], width=300)
#             except:
#                 st.write("🖼️ Image non disponible")
            
#     with col2:
#         st.title(product['title'])
#         st.write(f"💰 Prix: £{product['price']:.2f}")
#         st.write(f"⭐ Note: {product['stars']:.1f}/5 ({int(product['reviews']):,} avis)")
#         st.write(f"📁 Catégorie: {product['categoryName']}")
        
#         if pd.notna(product.get('productURL')):
#             st.markdown(f"[Voir sur Amazon]({product['productURL']})")
    
#     # Section des recommandations
#     st.markdown("---")
#     st.header("Produits similaires recommandés")
    
#     try:
#         recommender = AmazonRecommender()
#         recommender.fit(df)
        
#         recommendations = recommender.get_similar_products(product.name)
#         if not recommendations.empty:
#             cols = st.columns(3)
#             # for idx, rec in recommendations.iterrows():
#             #     with cols[idx % 3]:
#             #         # Image du produit
#             #         if pd.notna(rec.get('imgUrl')):
#             #             try:
#             #                 st.image(rec['imgUrl'], width=200)
#             #             except:
#             #                 st.write("🖼️ Image non disponible")
                    
#             # Dans la section affichage des recommandations
#             for idx, rec in recommendations.iterrows():
#                 with cols[idx % 3]:
#                     # Debug : afficher l'URL
#                     st.write("Debug - Infos produit:", rec.to_dict())
                    
#                     # Vérification et nettoyage de l'URL
#                     image_url = rec.get('imgUrl')
#                     st.write(f"Debug - URL image: {image_url}")
#                     if pd.notna(image_url):
#                         # Nettoyage de l'URL (enlever les espaces, etc.)
#                         image_url = str(image_url).strip()
#                         try:
#                             st.image(image_url, width=200)
#                         except Exception as e:
#                             st.write(f"🖼️ Image non disponible (Erreur: {str(e)})")
#                     else:
#                         st.write("🖼️ Aucune URL d'image")

   
#                     # Informations du produit
#                     st.markdown(f"**{rec.get('title', 'Titre non disponible')[:100]}...**")
#                     st.write(f"💰 Prix: £{rec.get('price', 0):.2f}")
#                     st.write(f"⭐ Note: {rec.get('stars', 0):.1f}/5 ({int(rec.get('reviews', 0)):,} avis)")
#                     st.write(f"📁 {rec.get('categoryName', 'Catégorie non disponible')}")
                    
#                     # Boutons et liens
#                     if pd.notna(rec.get('productURL')):
#                         st.markdown(f"[Voir sur Amazon]({rec['productURL']})")
#                     if st.button("Voir détails", key=f"rec_{idx}"):
#                         st.session_state.selected_product = pd.Series(rec)
#                         st.rerun()
#                     st.markdown("---")
#         else:
#             st.warning("Aucune recommandation trouvée pour ce produit.")
#     except Exception as e:
#         st.error(f"Erreur lors du chargement des recommandations: {str(e)}")




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

        # Dans la section principale (après le chargement des données)
        if st.session_state.current_page == 'main':
            st.title("🛍️ Système de Recommandation Amazon")
            
            recommender = AmazonRecommender()
            recommender.fit(df)
            st.success("Données chargées avec succès!")
            
            st.sidebar.write(f"Total produits: {len(df):,}")
            
            # Barre de recherche
            search_query = st.text_input("🔍 Rechercher un produit", "")
            
            # Initialisation avec les produits les plus populaires
            if not search_query:  # Si aucune recherche n'est effectuée
                filtered_df = df[
                    (df['stars'] >= 4.0) & 
                    (df['stars'] <= 5.0)
                ].copy()
                
                # Calcul du score de popularité
                filtered_df['popularity_score'] = filtered_df['stars'] * np.log1p(filtered_df['reviews'])
                filtered_df = filtered_df.sort_values('popularity_score', ascending=False)
                
                st.write("Produits les plus populaires:")
            else:
                # Code existant pour la recherche
                filtered_df = df.copy()
                mask = filtered_df['title'].str.contains(search_query, case=False, na=False)
                filtered_df = filtered_df[mask]
                st.write(f"Résultats pour '{search_query}': {len(filtered_df)} produits")
                
                mask = filtered_df['title'].str.contains(search_query, case=False, na=False)
                filtered_df = filtered_df[mask]
                st.write(f"Résultats pour '{search_query}': {len(filtered_df)} produits")
            
            categories = ["Toutes les catégories"] + sorted(df['categoryName'].unique().tolist())
            selected_category = st.sidebar.selectbox(
                "Sélectionnez une catégorie",
                categories
            )
            if selected_category != "Toutes les catégories":
                filtered_df = filtered_df[filtered_df['categoryName'] == selected_category]

            
            price_min = float(filtered_df['price'].min())
            price_max = float(filtered_df['price'].max())
            price_avg = float(filtered_df['price'].mean())
            price_range = st.sidebar.slider(
                "Gamme de prix (£)",
                min_value=price_min,
                max_value=price_max,
                value=(price_min, min(price_max, price_avg))
            )
            
            filtered_df = filtered_df[
                (filtered_df['price'] >= price_range[0]) &
                (filtered_df['price'] <= price_range[1])
            ]
            
            min_rating = st.sidebar.slider(
                "Note minimale",
                1.0, 5.0, 4.0, 0.5
            )
            
            avg_reviews = int(filtered_df["reviews"].mean())
            min_reviews = st.sidebar.number_input(
                "Nombre minimum d'avis",
                0,
                int(filtered_df['reviews'].max()),
                100
            )
            
            filtered_df = filtered_df[
                (filtered_df['stars'] >= min_rating) &
                (filtered_df['reviews'] >= avg_reviews)
            ]
            
            st.sidebar.write("Statistiques de filtrage:")
            st.sidebar.write(f"Produits affichés: {len(filtered_df):,}")
            
            sort_options = {
                "Les plus pertinents": lambda df: df['stars'] * np.log1p(df['reviews']),
                "Prix croissant": lambda df: df['price'],
                "Prix décroissant": lambda df: -df['price'],
                "Meilleures notes": lambda df: -df['stars'],
                "Plus d'avis": lambda df: -df['reviews']
            }

            sort_by = st.selectbox("Trier par", list(sort_options.keys()))
            filtered_df['sort_key'] = sort_options[sort_by](filtered_df)
            filtered_df = filtered_df.sort_values('sort_key', ascending=True)
            filtered_df = filtered_df.drop('sort_key', axis=1)
            
            if len(filtered_df) > 0:
                filtered_df = filtered_df.head(30)
                
                cols = st.columns(3)
                for idx, product in filtered_df.iterrows():
                    col_idx = idx % 3
                    with cols[col_idx]:
                        st.markdown("---")
                        if pd.notna(product['imgUrl']):
                            try:
                                st.image(product['imgUrl'], width=200)
                            except:
                                st.write("🖼️ Image non disponible")
                        st.markdown(f"**{product['title'][:100]}...**")
                        st.write(f"💰 Prix: £{product['price']:.2f}")
                        st.write(f"⭐ Note: {product['stars']:.1f}/5 ({int(product['reviews']):,} avis)")
                        st.write(f"📁 {product['categoryName']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if pd.notna(product['productURL']):
                                st.markdown(f"[Voir sur Amazon]({product['productURL']})")
                        with col2:
                            if st.button(f"Voir détails", key=f"prod_{idx}"):
                                st.session_state.selected_product = product
                                st.session_state.current_page = 'detail'
                                st.rerun()
            else:
                st.warning("Aucun produit ne correspond aux critères sélectionnés.")
        
        elif st.session_state.current_page == 'detail' and st.session_state.selected_product is not None:
            show_product_detail(st.session_state.selected_product, df)
            
    except Exception as e:
        st.error(f"Une erreur s'est produite: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Développé avec ❤️ par [Votre nom]")