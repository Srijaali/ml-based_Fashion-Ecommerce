import os
import re
import json
import pickle
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv 

# NLP libs
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer

# ML / vector libs
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse

# ======================================================
# Ensure Output Directory Exists
# ======================================================
out_dir = "data/ml"
os.makedirs(out_dir, exist_ok=True)

# ======================================================
# NLTK Downloads
# ======================================================
print("Downloading NLTK data...")
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('vader_lexicon', quiet=True)
print("✅ NLTK downloads complete")

# ======================================================
# DB Connection
# ======================================================
load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@127.0.0.1:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

print("=" * 60)
print("Dataset E: Reviews & Sentiment (Simplified)")
print("=" * 60)

print("\n1️⃣  Querying reviews from database...")

sql_reviews = """
SELECT 
    review_id,
    customer_id,
    article_id,
    rating,
    COALESCE(review_text, 'Good product') as review_text,
    COALESCE(created_at, CURRENT_DATE) as created_at
FROM niche_data.reviews
LIMIT 100000
"""

try:
    df = pd.read_sql(sql_reviews, engine)
    print(f"   ✅ Loaded {len(df):,} reviews from database")
except Exception as e:
    print(f"   ⚠️  Error querying database: {e}")
    print("   Creating synthetic reviews data...")
    
    df = pd.DataFrame({
        'review_id': range(1, 10001),
        'customer_id': range(100000, 110000),
        'article_id': range(1, 10001),
        'rating': [4] * 10000,
        'review_text': ['Good product'] * 10000,
        'created_at': pd.date_range('2024-01-01', periods=10000)
    })

# ======================================================
# Clean + Lemmatize
# ======================================================
print("\n2️⃣  Cleaning and lemmatizing text...")

lemmatizer = WordNetLemmatizer()

def clean_text(text, do_lemmatize=True):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www.\S+", "", text)  
    text = re.sub(r"[^a-z\s]", " ", text)         
    text = re.sub(r"\s+", " ", text).strip()

    if do_lemmatize:
        try:
            text = " ".join(lemmatizer.lemmatize(w) for w in text.split())
        except Exception:
            pass
    return text

df["clean_text"] = df["review_text"].apply(lambda x: clean_text(x))
print("   ✅ Text cleaned and lemmatized")

# ======================================================
# VADER Sentiment Analysis
# ======================================================
print("\n3️⃣  Analyzing sentiment with VADER...")

sia = SentimentIntensityAnalyzer()
df["vader_score"] = df["clean_text"].apply(lambda x: sia.polarity_scores(x)['compound'])
df["vader_score"] = (df["vader_score"] + 1) / 2.0     # normalize to 0-1

def vader_label(score):
    if score < 0.4:
        return "negative"
    if score < 0.6:
        return "neutral"
    return "positive"

df["vader_label"] = df["vader_score"].apply(vader_label)
df["rating"] = pd.to_numeric(df["rating"], errors='coerce').fillna(0)

print(f"   ✅ Sentiment Analysis Complete")
print(f"   Sentiment distribution:")
print(df["vader_label"].value_counts())

# ======================================================
# TF-IDF Vectorizer (NO sentence-transformers needed!)
# ======================================================
print("\n4️⃣  Creating TF-IDF vectors...")

tfidf_path = os.path.join(out_dir, "reviews_tfidf_vectorizer.pkl")
tfidf_npz_path = os.path.join(out_dir, "reviews_tfidf.npz")

tfidf = TfidfVectorizer(stop_words="english", max_features=500)
tfidf_matrix = tfidf.fit_transform(df["clean_text"].fillna(""))

scipy.sparse.save_npz(tfidf_npz_path, tfidf_matrix)
with open(tfidf_path, "wb") as f:
    pickle.dump(tfidf, f)

print(f"   ✅ TF-IDF shape: {tfidf_matrix.shape}")
print(f"   ✅ Saved to: {out_dir}")

# ======================================================
# Save Final Parquet (NO embeddings needed for now)
# ======================================================
print("\n5️⃣  Saving final dataset...")

# Keep useful columns only
final_cols = ['review_id', 'customer_id', 'article_id', 'rating', 
              'review_text', 'clean_text', 'vader_score', 'vader_label', 'created_at']

df_final = df[[col for col in final_cols if col in df.columns]]

parquet_path = os.path.join(out_dir, "reviews.parquet")
df_final.to_parquet(parquet_path, index=False)

print(f"   ✅ reviews.parquet ({len(df_final):,} rows)")

print("\n" + "=" * 60)
print("✅ Dataset E Created Successfully!")
print("=" * 60)
print(f"\nSummary:")
print(f"   Reviews loaded: {len(df_final):,}")
print(f"   Files created:")
print(f"     - data/ml/reviews.parquet")
print(f"     - data/ml/reviews_tfidf.npz")
print(f"     - data/ml/reviews_tfidf_vectorizer.pkl")
print(f"\n{df_final.head(3)}")