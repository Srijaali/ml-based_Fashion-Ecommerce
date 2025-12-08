import numpy as np
import faiss
import pandas as pd

class ProductSimilarity:
    def __init__(self):
        # Load product embeddings
        self.embeddings = np.load("models/embeddings/product_embeddings.npy")

        # Load FAISS index
        self.index = faiss.read_index("models/embeddings/faiss_product_index.index")

        # Load product ID mapping
        self.product_map = pd.read_parquet("models/embeddings/product_ids.parquet")

        # Convert to dicts for speed
        self.idx_to_pid = dict(zip(self.product_map.idx, self.product_map.product_id))
        self.pid_to_idx = dict(zip(self.product_map.product_id, self.product_map.idx))

    def get_similar_by_id(self, product_id, k=10):
        if product_id not in self.pid_to_idx:
            return None

        row_idx = self.pid_to_idx[product_id]

        query_vec = self.embeddings[row_idx].astype("float32").reshape(1, -1)
        distances, indices = self.index.search(query_vec, k + 1)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == row_idx:
                continue
            results.append({
                "product_id": self.idx_to_pid[idx],
                "similarity": float(1 - dist)
            })

        return results[:k]

product_sim = ProductSimilarity()
