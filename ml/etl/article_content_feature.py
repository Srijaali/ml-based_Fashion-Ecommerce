import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:rayyan123@localhost:5432/fashion_db")

query = """ 
WITH cat AS (
    SELECT 
        c1.category_id,
        c1.name AS category_name,
        c1.parent_category_id,
        CASE
            WHEN c1.parent_category_id IS NULL THEN 0
            WHEN c2.parent_category_id IS NULL THEN 1
            ELSE 2
        END AS category_depth
    FROM niche_data.categories c1
    LEFT JOIN niche_data.categories c2 ON c1.parent_category_id = c2.category_id
)

SELECT 
    a.article_id,
    a.product_code,
    a.prod_name,
    a.product_type_name,
    a.product_group_name,
    a.graphical_appearance_name,
    a.colour_group_name,
    a.department_name,
    a.index_name,
    a.section_name,
    a.garment_group_name,
    a.detail_desc,
    a.created_at,
    a.last_updated,
    a.price,
    a.stock,
    a.category_id,
    
    -- Category extra data
    cat.category_name,
    cat.parent_category_id,
    cat.category_depth,
    
    -- Lifecycle feature
    EXTRACT(DAY FROM (CURRENT_DATE - a.created_at)) AS lifecycle_days

FROM niche_data.articles a
LEFT JOIN cat ON a.category_id = cat.category_id;
"""

df = pd.read_sql(query, engine)

print(df.head())


from sklearn.preprocessing import RobustScaler

scaler = RobustScaler()
df['normalized_price'] = scaler.fit_transform(df[['price']])


from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

vectorizer = TfidfVectorizer(
    stop_words='english',
    max_features=5000,         # stable & efficient
    min_df=5                   # remove rare noise words
)

tfidf_matrix = vectorizer.fit_transform(df['detail_desc'].fillna(""))

# Save sparse matrix
import scipy.sparse
scipy.sparse.save_npz("data/ml/tfidf_detail_desc.npz", tfidf_matrix)

# Save vocabulary for later use
import pickle
pickle.dump(vectorizer, open("data/ml/tfidf_vectorizer.pkl", "wb"))


from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')  # 384-dim, fast

embeddings = model.encode(
    df['detail_desc'].fillna(""),
    batch_size=64,
    show_progress_bar=True
)

import numpy as np
np.save("data/ml/bert_embeddings.npy", embeddings)


df.to_parquet("data/ml/articles_structured.parquet", index=False)
# df.to_csv("data/ml/articles_structured.csv", index=False)




