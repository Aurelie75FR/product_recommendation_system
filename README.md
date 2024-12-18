# Amazon Product Recommendation System

## 📋 Overview
A content-based recommendation system developed to suggest Amazon products to users, leveraging machine learning to provide personalized product recommendations.

## 💼 Business Case
In a world saturated with information and options, recommendation systems enable companies to:
- Improve user experience by facilitating product discovery
- Increase sales and engagement through targeted suggestions
- Build customer loyalty through personalized experiences

Giants like Netflix, Amazon, Spotify, Steam, and others have demonstrated the strategic impact of recommendations on revenue growth and user satisfaction.

## 🏗️ Project Architecture

### Main Components:
1. **Exploration and Cleaning**
   - Dataset processing (2M+ rows)
   - Null/NaN values removal

2. **EDA (Exploratory Data Analysis)**
   - Category Distribution
   - Number of Products per Category
   - Average prices per category
   - Average scores by category
   - Best-Sellers by Category

3. **Recommendation System**
   - ML model: K-Nearest Neighbors (KNN)
   - Category Similarity
   - Normalized & Segmentation of products
   - Similar Products based on:
     * Price
     * Rating
     * Reviews

4. **Evaluation Metrics**
   - Evaluation System
   - Diversity Metrics
   - Relevance Metrics
   - Coverage Metrics

## 🔧 Technical Stack
- Python
- Pandas & NumPy for data processing
- Scikit-learn for ML (KNN model)
- Streamlit for web interface

## 💫 Features
- Content-based recommendation system
- KNN algorithm for finding similar products
- Interactive web interface with Streamlit
- Product filtering and sorting capabilities
- Detailed product views with recommendations

## 🚀 Why KNN?
- Simple and interpretable model
- Efficient for finding similar items
- Works well with normalized feature spaces
- Adapts instantly to new data
- Perfect for structured e-commerce data
- Balances similarity and diversity in recommendations

## 🎯 Future Improvements
- Enhanced search functionality
- Improved filtering system
- More user-friendly interface
- New segmentation: Create major categories with product sub-categories for greater diversity in recommendations

## 🖥️ Interface
The project features a Streamlit web interface that allows users to:
- Browse products by category
- Search for specific items
- View detailed product information
- Get personalized product recommendations
- Filter and sort products based on various criteria

## 🔄 Project Workflow
1. Data loading and preprocessing
2. Feature engineering and normalization
3. KNN model implementation
4. Recommendation generation
5. Web interface interaction
6. Metrics evaluation and monitoring

## 📈 Evaluation
The system is evaluated based on:
- Diversity of recommendations
- Relevance to user queries
- Coverage of product catalog
- Response time and performance

## 🛠️ Setup and Installation
 
<details>
1. **Clone the repository**:

```bash
git clone https://github.com/YourUsername/repository_name.git
```

2. **Install UV**

If you're a MacOS/Linux user type:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If you're a Windows user open an Anaconda Powershell Prompt and type :

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. **Create an environment**

```bash
uv venv 
```

3. **Activate the environment**

If you're a MacOS/Linux user type (if you're using a bash shell):

```bash
source ./venv/bin/activate
```

If you're a MacOS/Linux user type (if you're using a csh/tcsh shell):

```bash
source ./venv/bin/activate.csh
```

If you're a Windows user type:

```bash
.\venv\Scripts\activate
```

4. **Install dependencies**:

```bash
uv pip install -r requirements.txt
```
</details>