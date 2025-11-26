import os
import re
import pickle
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# NLP libs
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer

# ML / vector libs
from detoxify import Detoxify
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse
from sentence_transformers import SentenceTransformer

# ---------------------------
# Ensure output dirs exist
out_dir = "data/ml"
os.makedirs(out_dir, exist_ok=True)

# ---------------------------
# Download required nltk assets (safe to call repeatedly)
# wordnet -> lemmatizer, omw-1.4 improves lemmatization coverage
# vader_lexicon -> VADER sentiment analyzer
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('vader_lexicon', quiet=True)

# ---------------------------
# DB connection
engine = create_engine("postgresql://postgres:rayyan123@localhost:5432/fashion_db")

sql_reviews = '''
SELECT 
    r.review_id,
    r.customer_id,
    r.article_id,
    a.category_id,
    r.rating,
    r.review_text,
    r.created_at,
    EXTRACT(DAY FROM (CURRENT_DATE - r.created_at)) AS review_age_days
FROM niche_data.reviews r
LEFT JOIN niche_data.articles a ON r.article_id = a.article_id;
'''

df = pd.read_sql(sql_reviews, engine)

# ---------------------------
# Text cleaning + lemmatization
lemmatizer = WordNetLemmatizer()

def clean_text(text, do_lemmatize=True):
    # safe guard non-strings
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www.\S+", "", text)     # remove urls
    text = re.sub(r"[^a-z\s]", " ", text)           # keep letters + spaces
    text = re.sub(r"\s+", " ", text)                # collapse whitespace
    text = text.strip()
    if do_lemmatize:
        try:
            text = " ".join(lemmatizer.lemmatize(word) for word in text.split())
        except Exception:
            # If wordnet somehow unavailable, fallback to original cleaned text
            pass
    return text

# Apply cleaning; if WordNet not downloaded, still works (we downloaded above)
df['clean_text'] = df['review_text'].apply(lambda x: clean_text(x, do_lemmatize=True))

# ---------------------------
# Sentiment (VADER)
sia = SentimentIntensityAnalyzer()
df['sentiment_score'] = df['clean_text'].apply(lambda x: sia.polarity_scores(x)['compound'])
# Normalize from [-1,1] to [0,1]
df['sentiment_score'] = (df['sentiment_score'] + 1) / 2.0

def label(score):
    if score < 0.4:
        return "negative"
    if score < 0.6:
        return "neutral"
    return "positive"

df['sentiment_label'] = df['sentiment_score'].apply(label)

'''
# ---------------------------
# Toxicity detection (Detoxify) - wrap in try/except to avoid hard crash if model fails to load
try:
    tox = Detoxify('original')  # may download model weights on first call
    # Detoxify.predict can accept a list
    texts = df['review_text'].fillna("").tolist()
    tox_scores = tox.predict(texts)
    # tox_scores is dict-like with arrays for keys like 'toxicity', 'severe_toxicity'...
    # If Detoxify returns arrays, convert accordingly:
    df['toxicity'] = tox_scores.get('toxicity')
    df['severe_toxicity'] = tox_scores.get('severe_toxicity')
    # If detoxify returns a single dict per-call (older versions), handle fallback:
    if isinstance(df['toxicity'].iloc[0], (list, np.ndarray)):
        # Already column filled with arrays? unlikely but safe-check
        pass
    print("Detoxify: toxicity columns created.")
except Exception as e:
    print("Warning: Detoxify failed or could not load model. Continuing without toxicity scores.")
    print("Detoxify error:", str(e))
    df['toxicity'] = np.nan
    df['severe_toxicity'] = np.nan
'''
    
# ---------------------------
# TF-IDF Vectorization
tfidf_path = os.path.join(out_dir, "reviews_tfidf_vectorizer.pkl")
tfidf_npz_path = os.path.join(out_dir, "reviews_tfidf.npz")

tfidf = TfidfVectorizer(stop_words='english', max_features=7000)
tfidf_matrix = tfidf.fit_transform(df['clean_text'].fillna("").tolist())

# Save sparse matrix and vectorizer
scipy.sparse.save_npz(tfidf_npz_path, tfidf_matrix)
with open(tfidf_path, "wb") as f:
    pickle.dump(tfidf, f)

print("TF-IDF matrix shape:", tfidf_matrix.shape)
print("Saved TF-IDF vectorizer and matrix to:", out_dir)

# ---------------------------
# Sentence-BERT embeddings
emb_path = os.path.join(out_dir, "reviews_bert_embeddings.npy")
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(
        df['clean_text'].fillna("").tolist(),
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    np.save(emb_path, embeddings)
    print("Saved BERT embeddings:", emb_path, " shape:", embeddings.shape)
except Exception as e:
    print("Warning: SentenceTransformer failed to load or encode. Error:", str(e))

# ---------------------------
# Save dataframe as parquet
parquet_path = os.path.join(out_dir, "reviews.parquet")
df.to_parquet(parquet_path, index=False)
print("Saved reviews dataframe to:", parquet_path)

# Optional: a small head preview
print(df.head(3).T)
