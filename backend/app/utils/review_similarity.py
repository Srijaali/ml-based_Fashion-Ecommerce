import numpy as np
import faiss
import pandas as pd

class ReviewSimilarity:
    def __init__(self):
        # Load embeddings
        self.embeddings = np.load("models/embeddings/review_embeddings.npy")

        # Load FAISS index
        self.index = faiss.read_index("models/embeddings/faiss_review_index.index")

        # Load mapping review_id -> row index
        self.review_map = pd.read_parquet("models/embeddings/review_ids.parquet")
        # review_map columns: ["review_id", "idx"]

        # To speed lookup
        self.id_to_idx = dict(zip(self.review_map.review_id, self.review_map.idx))
        self.idx_to_id = dict(zip(self.review_map.idx, self.review_map.review_id))

    def get_similar_by_id(self, review_id, k=10):
        if review_id not in self.id_to_idx:
            return None

        row_idx = self.id_to_idx[review_id]

        query_vec = self.embeddings[row_idx].astype("float32").reshape(1, -1)
        distances, indices = self.index.search(query_vec, k + 1)  # includes itself

        # Filter out the review itself
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == row_idx:
                continue
            results.append({
                "similar_review_id": self.idx_to_id[idx],
                "score": float(1 - dist)   # convert FAISS distance to similarity
            })

        return results[:k]

    def get_similar_by_text(self, text, model, k=10):
        # Encode new text
        emb = model.encode([text], convert_to_numpy=True).astype("float32")

        distances, indices = self.index.search(emb, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            results.append({
                "review_id": self.idx_to_id[idx],
                "score": float(1 - dist)
            })
        return results

review_sim = ReviewSimilarity()
