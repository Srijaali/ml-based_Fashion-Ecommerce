import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

os.makedirs("data/ml", exist_ok=True)
load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@127.0.0.1:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

print("=" * 60)
print("Dataset C: Customer Features (RFM Analysis)")
print("=" * 60)

# RFM Analysis
print("\n1️⃣  Querying customer transactions...")

# ⭐ FIXED: Add niche_data. schema prefix
query = """
SELECT 
    c.customer_id,
    COALESCE(c.age, 30) as age,
    COUNT(DISTINCT t.customer_id) as frequency,
    COALESCE(SUM(t.price), 0) as monetary,
    COALESCE(MAX(t.t_dat), CURRENT_DATE) as last_purchase_date
FROM niche_data.customers c
LEFT JOIN niche_data.transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.age
LIMIT 500000
"""

df = pd.read_sql(query, engine)
print(f"   Loaded {len(df)} customers")

# Calculate Recency
print("\n2️⃣  Calculating RFM scores...")
today = datetime.now()
df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'])
df['recency'] = (today - df['last_purchase_date']).dt.days
df['recency'] = df['recency'].fillna(999)

# Scoring (1-5)
df['R_score'] = pd.qcut(df['recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
df['F_score'] = pd.qcut(df['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
df['M_score'] = pd.qcut(df['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

# Convert to numeric
df['R_score'] = pd.to_numeric(df['R_score'])
df['F_score'] = pd.to_numeric(df['F_score'])
df['M_score'] = pd.to_numeric(df['M_score'])

df['rfm_score'] = df['R_score'] + df['F_score'] + df['M_score']

print(f"   RFM Score Range: {df['rfm_score'].min():.0f} - {df['rfm_score'].max():.0f}")

# Save
print("\n3️⃣  Saving file...")
df.to_parquet('data/ml/customer_features.parquet', index=False)
print("   ✅ customer_features.parquet")

print("\n" + "=" * 60)
print("✅ Dataset C Created Successfully!")
print("=" * 60)
print(f"   Shape: {df.shape}")
print(f"   Location: data/ml/customer_features.parquet")