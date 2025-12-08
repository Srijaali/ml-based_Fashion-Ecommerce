import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import joblib

class ComplaintExtractor:
    def __init__(self):
        # Load the full preprocessed reviews dataframe
        self.df = pd.read_parquet("data/ml/reviews/reviews_preprocessed/reviews_preprocessed.parquet")

        # Load TF-IDF vectorizer
        self.vectorizer = joblib.load("models/sentiment/reviews_tfidf_vectorizer.pkl")

        # Ensure all needed columns exist
        required = {"clean_text", "sentiment_label", "article_id"}
        if not required.issubset(self.df.columns):
            raise ValueError("Missing required columns in reviews_preprocessed")

        # Load article -> category mapping
        self.article_map = pd.read_parquet("data/ml/product_review_features.parquet")[["article_id", "category_id"]]
        self.df = self.df.merge(self.article_map, on="article_id", how="left")

    def get_top_complaints(self, category_id, top_n=15):
        df_cat = self.df[self.df["category_id"] == category_id]

        if df_cat.empty:
            return None

        # Filter negative + neutral reviews for complaints
        df_neg = df_cat[df_cat["sentiment_label"].isin(["negative", "neutral"])]

        if df_neg.empty:
            return []

        texts = df_neg["clean_text"].tolist()

        # Compute TF-IDF matrix
        tfidf = self.vectorizer.transform(texts)
        scores = np.asarray(tfidf.sum(axis=0)).ravel()

        feature_names = self.vectorizer.get_feature_names_out()
        top_idx = scores.argsort()[::-1][:top_n]

        complaints = [
            {"keyword": feature_names[i], "score": float(scores[i])}
            for i in top_idx
        ]

        # Get example reviews for context
        example_reviews = df_neg[["review_text", "sentiment_label"]].head(10).to_dict(orient="records")

        return complaints, example_reviews


complaint_extractor = ComplaintExtractor()
