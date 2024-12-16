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


def calculate_search_relevance(row, search_terms, exact_phrase=False):
    """
    Calcule un score de pertinence basé sur les termes de recherche et les caractéristiques des produits.
    """
    title = str(row['title']).lower()
    category = str(row['categoryName']).lower()
    score = 0

    # Diviser les termes de recherche en mots-clés
    search_terms = [term.lower() for term in search_terms.split()]
    
    # Boost si tous les mots-clés apparaissent dans le titre
    if all(term in title for term in search_terms):
        score += 100
        if exact_phrase and search_terms[0] in title:
            score += 50

    # Pénalisation pour les accessoires ou produits compatibles
    accessory_keywords = [
        'cable', 'case', 'cover', 'accessory', 'accessories', 'stand', 
        'mount', 'holder', 'protector', 'aux', 'adapter', 'compatible', 'for'
    ]
    if any(word in title for word in accessory_keywords):
        score -= 100

    # Bonus pour la correspondance exacte de la catégorie
    if any(term in category for term in search_terms):
        score += 50

    # Prendre en compte les notes et les avis
    score += min(row['stars'], 5)
    score += min(np.log1p(row['reviews']) / 20, 2.5)
    
    return max(score, 0)


# def show_product_detail(product, df):
#     """
#     render product page details
#     """
#     # Back btn
#     if st.button("← Back to Result"):
#         st.session_state.current_page = 'main'
#         st.rerun()

#     # Select product details
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         if pd.notna(product.get('imgUrl')):
#             try:
#                 st.image(product['imgUrl'], width=300)
#             except:
#                 st.write("🖼️ Image not available")
            
#     with col2:
#         st.title(product['title'])
#         st.write(f"💰 Price: £{product['price']:.2f}")
#         st.write(f"⭐ Rating: {product['stars']:.1f}/5 ({int(product['reviews']):,} avis)")
#         st.write(f"📁 Category: {product['categoryName']}")
        
#         if pd.notna(product.get('productURL')):
#             st.markdown(f"[See on Amazon]({product['productURL']})")

#     # Recommendations section
#     st.markdown("---")
#     st.header("Recommended similar products")
    
#     try:
#         # Init recommender
#         recommender = AmazonRecommender()
#         recommender.fit(df)
        
#         # Get recommendations
#         recommendations = recommender.get_similar_products(product.name)
        
#         if not recommendations.empty:
#             # Affichage en grille des recommandations
#             cols = st.columns(3)
#             for idx, rec in recommendations.iterrows():
#                 with cols[idx % 3]:
#                     # Image du produit
# #                     # Debug 
# #                     st.write("Debug - Infos produit:", rec.to_dict())
#                     if pd.notna(rec.get('imgUrl')):
#                         try:
#                             st.image(rec['imgUrl'], width=200)
#                         except:
#                             st.write("🖼️ Image not available")
                    
#                     # Informations du produit
#                     st.markdown(f"**{rec['title'][:100]}...**")
#                     st.write(f"💰 Price: £{rec['price']:.2f}")
#                     st.write(f"⭐ Rating: {rec['stars']:.1f}/5 ({int(rec['reviews']):,} avis)")
#                     st.write(f"📁 {rec['categoryName']}")
                    
#                     # Liens et actions
#                     col1, col2 = st.columns([1, 1])
#                     with col1:
#                         if pd.notna(rec.get('productURL')):
#                             st.markdown(f"[See on Amazon]({rec['productURL']})")
#                     with col2:
#                         if st.button("See details", key=f"rec_{idx}"):
#                             st.session_state.selected_product = rec
#                             st.rerun()
                    
#                     st.markdown("---")
#         else:
#             st.warning("No recommendations found for this product.")
            
#     except Exception as e:
#         st.error(f"Error when loading recommendations: {str(e)}")

def show_product_detail(product, df):
    """
    render product page details
    """
    # Back btn
    if st.button("← Back to Result"):
        st.session_state.current_page = 'main'
        st.rerun()

    # Select product details
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if pd.notna(product.get('imgUrl')):
            try:
                st.image(product['imgUrl'], width=300)
            except:
                st.write("🖼️ Image not available")
            
    with col2:
        st.title(product['title'])
        st.write(f"💰 Price: £{product['price']:.2f}")
        st.write(f"⭐ Rating: {product['stars']:.1f}/5 ({int(product['reviews']):,} reviews)")
        st.write(f"📁 Category: {product['categoryName']}")
        
        if pd.notna(product.get('productURL')):
            st.markdown(f"[See on Amazon]({product['productURL']})")

    # Recommendations section
    st.markdown("---")
    st.header("Recommended similar products")
    
    # Style CSS pour le conteneur de produit
    product_container_style = """
        <style>
            .product-card {
                height: 300px;
                width : auto;
                padding: 1rem;
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 0.05);
                margin-bottom: 1rem;
            }
            .product-image {
                height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .product-image img {
                max-height: 200px;
                width: auto;
                object-fit: contain;
            }
        </style>
    """
    st.markdown(product_container_style, unsafe_allow_html=True)
    
    try:
        recommender = AmazonRecommender()
        recommender.fit(df)
        
        recommendations = recommender.get_similar_products(product.name)
        
        if not recommendations.empty:
            cols = st.columns(3)
            for idx, rec in recommendations.iterrows():
                with cols[idx % 3]:
                    # Carte produit avec image
                    st.markdown("""
                        <div class="product-card">
                            <div class="product-image">
                                <img src="{}" alt="product image">
                            </div>
                        </div>
                    """.format(rec['imgUrl'] if pd.notna(rec.get('imgUrl')) else ""), unsafe_allow_html=True)
                    
                    # Informations produit
                    st.markdown(f"**{rec['title'][:100]}...**")
                    st.write(f"💰 Price: £{rec['price']:.2f}")
                    st.write(f"⭐ Rating: {rec['stars']:.1f}/5 ({int(rec['reviews']):,} reviews)")
                    st.write(f"📁 {rec['categoryName']}")
                    
                    # Actions
                    col1, col2 = st.columns(2)
                    with col1:
                        if pd.notna(rec.get('productURL')):
                            st.markdown(f"[See on Amazon]({rec['productURL']})")
                    with col2:
                        if st.button("See details", key=f"rec_{idx}"):
                            st.session_state.selected_product = rec
                            st.rerun()
        else:
            st.warning("No recommendations found for this product.")
            
    except Exception as e:
        st.error(f"Error when loading recommendations: {str(e)}")


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
        st.error(f"Error when loading data: {str(e)}")
        return None

# Chargement des données
df = load_data()

if df is not None:
    try:

        # Dans la section principale (après le chargement des données)
        if st.session_state.current_page == 'main':
            st.title("🛍️ Recommendation system with Amazon products")
            
            recommender = AmazonRecommender()
            recommender.fit(df)
            st.success("Data successfully loaded!")
            
            st.sidebar.write(f"Total products: {len(df):,}")
            
            # Barre de recherche
            search_query = st.text_input("🔍 Product search", "")
            
            # Initialisation avec les produits les plus populaires
            if not search_query:  # Si aucune recherche n'est effectuée
                filtered_df = df[
                    (df['stars'] >= 4.0) & 
                    (df['stars'] <= 5.0)
                ].copy()
                
                # Calcul du score de popularité
                filtered_df['popularity_score'] = filtered_df['stars'] * np.log1p(filtered_df['reviews'])
                filtered_df = filtered_df.sort_values('popularity_score', ascending=False)
                
            else:
             
                filtered_df = df.copy()
                mask = filtered_df['title'].str.contains(search_query, case=False, na=False)
                filtered_df = filtered_df[mask]
                st.write(f"Results for '{search_query}': {len(filtered_df)} products")
                
                mask = filtered_df['title'].str.contains(search_query, case=False, na=False)
                filtered_df = filtered_df[mask]
                st.write(f"Results for '{search_query}': {len(filtered_df)} products")
            
            categories = ["All categories"] + sorted(df['categoryName'].unique().tolist())
            selected_category = st.sidebar.selectbox(
                "Select category",
                categories
            )
            if selected_category != "All categories":
                filtered_df = filtered_df[filtered_df['categoryName'] == selected_category]

            
            price_min = float(filtered_df['price'].min())
            price_max = float(filtered_df['price'].max())
            price_avg = float(filtered_df['price'].mean())
            price_median = float(filtered_df['price'].median())
            price_range = st.sidebar.slider(
                "Price range (£)",
                min_value=price_min,
                max_value=price_max,
                value=(price_min, min(price_max, 300.0))
            )
            
            filtered_df = filtered_df[
                (filtered_df['price'] >= price_range[0]) &
                (filtered_df['price'] <= price_range[1])
            ]
            
            min_rating = st.sidebar.slider(
                "Minimum rating",
                1.0, 5.0, 4.0, 0.5
            )
            
            avg_reviews = int(filtered_df["reviews"].mean())
            min_reviews = st.sidebar.number_input(
                "Minimum number of reviews",
                0,
                int(filtered_df['reviews'].max()),
                100
            )
            
            filtered_df = filtered_df[
                (filtered_df['stars'] >= min_rating) &
                (filtered_df['reviews'] >= avg_reviews)
            ]
            
            st.sidebar.write("Filtering statistics:")
            st.sidebar.write(f"Products displayed: {len(filtered_df):,}")
            
            sort_options = {
                "Most relevant": lambda df: df['stars'] * np.log1p(df['reviews']),
                "By ascending price": lambda df: df['price'],
                "By descending price": lambda df: -df['price'],
                "Top ratings": lambda df: -df['stars'],
                "More reviews": lambda df: -df['reviews']
            }

            sort_by = st.selectbox("Sort by", list(sort_options.keys()))
            filtered_df['sort_key'] = sort_options[sort_by](filtered_df)
            filtered_df = filtered_df.sort_values('sort_key', ascending=True)
            filtered_df = filtered_df.drop('sort_key', axis=1)
            
            st.write("Most popular products:")


            # Dans la section d'affichage des produits
            if len(filtered_df) > 0:
                filtered_df = filtered_df.head(30)
                
                # Style CSS pour le conteneur de produit
                product_container_style = """
                    <style>
                        .product-card {
                            height: 300px;
                            padding: 1rem;
                            border-radius: 10px;
                            background-color: rgba(255, 255, 255, 0.05);
                            margin-bottom: 1rem;
                        }
                        .product-image {
                            height: 200px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        }
                        .product-image img {
                            max-height: 200px;
                            width: auto;
                            object-fit: contain;
                        }
                    </style>
                """
                st.markdown(product_container_style, unsafe_allow_html=True)
                
                cols = st.columns(3)
                for idx, product in filtered_df.iterrows():
                    col_idx = idx % 3
                    with cols[col_idx]:
                        st.markdown("""
                            <div class="product-card">
                                <div class="product-image">
                                    <img src="{}" alt="product image">
                                </div>
                            </div>
                        """.format(product['imgUrl'] if pd.notna(product['imgUrl']) else ""), unsafe_allow_html=True)
                        
                        # Informations du produit
                        st.markdown(f"**{product['title'][:100]}...**")
                        st.write(f"💰 Price: £{product['price']:.2f}")
                        st.write(f"⭐ Rating: {product['stars']:.1f}/5 ({int(product['reviews']):,} reviews)")
                        st.write(f"📁 {product['categoryName']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if pd.notna(product['productURL']):
                                st.markdown(f"[See on Amazon]({product['productURL']})")
                        with col2:
                            if st.button(f"See details", key=f"prod_{idx}"):
                                st.session_state.selected_product = product
                                st.session_state.current_page = 'detail'
                                st.rerun()
            else:
                st.warning("No products match the selected criteria.")
        
        elif st.session_state.current_page == 'detail' and st.session_state.selected_product is not None:
            show_product_detail(st.session_state.selected_product, df)
            
    except Exception as e:
        st.error(f"An error has occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ By Aurélie")