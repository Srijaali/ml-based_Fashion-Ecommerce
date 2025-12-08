import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import io
import base64

class WordCloudGenerator:
    def __init__(self):
        self.df = pd.read_parquet("data/ml/reviews/reviews_processed/reviews_preprocessed.parquet")
        # Ensure clean_text exists
        if "clean_text" not in self.df.columns:
            raise ValueError("clean_text column is missing in reviews_preprocessed.parquet")

        self.out_dir = "app/static/wordclouds"
        os.makedirs(self.out_dir, exist_ok=True)

    def generate_for_product(self, product_id):
        subset = self.df[self.df["article_id"] == product_id]

        if subset.empty:
            return None

        # Combine all clean text
        text = " ".join(subset["clean_text"].tolist())

        # Create the wordcloud
        wc = WordCloud(
            width=1000,
            height=600,
            background_color="white",
            max_words=200
        ).generate(text)

        # Save to file
        filepath = os.path.join(self.out_dir, f"{product_id}.png")
        wc.to_file(filepath)

        return filepath

    def generate_base64(self, product_id):
        subset = self.df[self.df["article_id"] == product_id]

        if subset.empty:
            return None

        text = " ".join(subset["clean_text"].tolist())

        wc = WordCloud(
            width=1000,
            height=600,
            background_color="white",
            max_words=200
        ).generate(text)

        img_buffer = io.BytesIO()
        wc.to_image().save(img_buffer, format="PNG")
        img_buffer.seek(0)

        img_base64 = base64.b64encode(img_buffer.read()).decode("utf-8")
        return img_base64


wordcloud_gen = WordCloudGenerator()
