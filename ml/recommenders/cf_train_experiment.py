"""
Fast Experimentation Script for Collaborative Filtering
Use this to test hyperparameters quickly (1-2 min per run)
Then use cf_train_simple.py for production training

=== HOW TO USE ===
1. Modify the HYPERPARAMETERS section below
2. Run: python ml/recommenders/cf_train_experiment.py
3. Check the metrics
4. Adjust hyperparameters and repeat
5. Once happy, update cf_train_simple.py with best values
"""

import pandas as pd
import numpy as np
import time
import pickle
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from scipy.sparse import csr_matrix, save_npz
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

# ============================================================================
# 🎯 EXPERIMENT HYPERPARAMETERS (MODIFY THESE!)
# ============================================================================

# Matrix factorization
N_COMPONENTS = 50              # Try: 20, 30, 50, 75, 100
SVD_ITERATIONS = 50            # Try: 20, 50, 100 (more = better quality, slower)

# Data sampling (for fast iteration)
DATA_SAMPLE_PERCENT = 10       # 10% = fast, 100% = full data. Start with 10!

# Recommendation generation
N_SIMILAR_USERS = 20           # Try: 10, 20, 50
N_SIMILAR_ITEMS = 20           # Try: 10, 20, 30
N_USERS_FOR_RECS = 100         # How many users to generate recs for (fast feedback)

# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'ml'
OUTPUT_DIR = PROJECT_ROOT / 'data' / 'recommendations'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("⚡ COLLABORATIVE FILTERING - FAST EXPERIMENT")
print("="*80)
print(f"\n🎯 HYPERPARAMETERS (modify in the script):")
print(f"  N_COMPONENTS: {N_COMPONENTS}")
print(f"  SVD_ITERATIONS: {SVD_ITERATIONS}")
print(f"  DATA_SAMPLE_PERCENT: {DATA_SAMPLE_PERCENT}%")
print(f"  N_SIMILAR_USERS: {N_SIMILAR_USERS}")
print(f"  N_SIMILAR_ITEMS: {N_SIMILAR_ITEMS}")
print(f"  N_USERS_FOR_RECS: {N_USERS_FOR_RECS}")
print()

start_total = time.time()

# ============================================================================
# STEP 1-2: Load & Build Matrix (SAMPLED)
# ============================================================================
print("[STEP 1-2] Loading data...")
start = time.time()

dataset_a = pd.read_parquet(DATA_DIR / 'user_item_interactions.parquet')
original_size = len(dataset_a)

# SAMPLE DATA FOR FAST ITERATION
if DATA_SAMPLE_PERCENT < 100:
    sample_size = int(len(dataset_a) * DATA_SAMPLE_PERCENT / 100)
    dataset_a = dataset_a.sample(n=sample_size, random_state=42)
    print(f"  Sampled {DATA_SAMPLE_PERCENT}%: {original_size:,} → {len(dataset_a):,} rows")
else:
    print(f"  Using all data: {len(dataset_a):,} rows")

# Create mappings
customers = dataset_a['customer_id'].unique()
articles = dataset_a['article_id'].unique()
customer_mapping = {cid: idx for idx, cid in enumerate(customers)}
article_mapping = {aid: idx for idx, aid in enumerate(articles)}
reverse_customer = {idx: cid for cid, idx in customer_mapping.items()}
reverse_article = {idx: aid for aid, idx in article_mapping.items()}

print(f"  Users: {len(customers):,}")
print(f"  Items: {len(articles):,}")

# Map indices
dataset_a['customer_idx'] = dataset_a['customer_id'].map(customer_mapping)
dataset_a['article_idx'] = dataset_a['article_id'].map(article_mapping)

# Build sparse matrix
user_item_matrix = csr_matrix(
    (dataset_a['time_weighted_score'].values,
     (dataset_a['customer_idx'].values, dataset_a['article_idx'].values)),
    shape=(len(customer_mapping), len(article_mapping))
)

n_users, n_items = user_item_matrix.shape
sparsity = 1 - (user_item_matrix.nnz / (n_users * n_items))
print(f"  Matrix: {n_users:,} × {n_items:,}")
print(f"  Sparsity: {sparsity:.2%}")
print(f"⏱️  {time.time() - start:.1f}s\n")

# ============================================================================
# STEP 3: SVD (The Main Experiment Variable)
# ============================================================================
print(f"[STEP 3] SVD ({N_COMPONENTS} components, {SVD_ITERATIONS} iterations)...")
start = time.time()

svd = TruncatedSVD(n_components=N_COMPONENTS, n_iter=SVD_ITERATIONS, random_state=42)
user_latent = svd.fit_transform(user_item_matrix)
item_latent = svd.components_.T
explained_var = svd.explained_variance_ratio_.sum()

print(f"  User factors: {user_latent.shape}")
print(f"  Item factors: {item_latent.shape}")
print(f"  🎯 Variance explained: {explained_var:.2%}")
print(f"⏱️  {time.time() - start:.1f}s\n")

# ============================================================================
# STEP 4: Item Similarity
# ============================================================================
print("[STEP 4] Item similarity...")
start = time.time()

item_similarity = cosine_similarity(item_latent)
print(f"  Shape: {item_similarity.shape}")
print(f"⏱️  {time.time() - start:.1f}s\n")

# ============================================================================
# STEP 5: KNN Index
# ============================================================================
print("[STEP 5] Building KNN...")
start = time.time()

k_neighbors = min(N_SIMILAR_USERS + 1, n_users)
knn = NearestNeighbors(n_neighbors=k_neighbors, metric='cosine', n_jobs=-1)
knn.fit(user_latent)

print(f"⏱️  {time.time() - start:.1f}s\n")

# ============================================================================
# STEP 6: Generate Sample Recommendations (FAST)
# ============================================================================
print(f"[STEP 6] Generating recommendations for {N_USERS_FOR_RECS} sample users...")
start = time.time()

user_indices = np.random.choice(n_users, min(N_USERS_FOR_RECS, n_users), replace=False)
distances, indices = knn.kneighbors(user_latent[user_indices])

all_recs = []
for i, user_idx in enumerate(user_indices):
    user_id = reverse_customer[user_idx]
    
    # Get similar users (skip self)
    similar_indices = indices[i][1:N_SIMILAR_USERS+1]
    similar_ids = [reverse_customer[idx] for idx in similar_indices]
    
    # Get user's current items
    user_items = set(dataset_a[dataset_a['customer_id'] == user_id]['article_id'])
    
    # Get similar users' purchases
    similar_purchases = dataset_a[dataset_a['customer_id'].isin(similar_ids)]
    candidates = similar_purchases[~similar_purchases['article_id'].isin(user_items)]
    
    if not candidates.empty:
        top_items = candidates.groupby('article_id')['time_weighted_score'].sum().nlargest(10)
        for rank, (article_id, score) in enumerate(top_items.items(), 1):
            all_recs.append({
                'customer_id': user_id,
                'article_id': article_id,
                'cf_score': float(score),
                'rank': rank
            })

if all_recs:
    user_recs_df = pd.DataFrame(all_recs)
    print(f"  Generated {len(user_recs_df):,} recommendations")
    print(f"  For {user_recs_df['customer_id'].nunique()} users")
    print(f"  Avg per user: {len(user_recs_df)/user_recs_df['customer_id'].nunique():.1f}")
else:
    print(f"  ⚠️  No recommendations generated")

print(f"⏱️  {time.time() - start:.1f}s\n")

# ============================================================================
# STEP 7: Item-Item Similarity (Quick Sample)
# ============================================================================
print(f"[STEP 7] Item similarities (sampling {min(500, n_items)} items)...")
start = time.time()

n_sample_items = min(500, n_items)
all_item_recs = []

for article_idx in range(n_sample_items):
    article_id = reverse_article[article_idx]
    similarities = item_similarity[article_idx]
    
    # Get top similar items
    top_indices = np.argsort(similarities)[-(N_SIMILAR_ITEMS+1):-1][::-1]
    
    for rank, similar_idx in enumerate(top_indices, 1):
        sim_score = similarities[similar_idx]
        if sim_score >= 0.1:
            all_item_recs.append({
                'article_id': article_id,
                'similar_article_id': reverse_article[similar_idx],
                'similarity_score': float(sim_score),
                'rank': rank
            })

if all_item_recs:
    item_recs_df = pd.DataFrame(all_item_recs)
    print(f"  Generated {len(item_recs_df):,} item pairs")
else:
    print(f"  ⚠️  No item recommendations")

print(f"⏱️  {time.time() - start:.1f}s\n")

# ============================================================================
# Results Summary
# ============================================================================
total_time = time.time() - start_total

print("="*80)
print("✅ EXPERIMENT COMPLETE")
print("="*80)

print(f"\n⏱️  Total Time: {total_time:.1f}s ({total_time/60:.2f} min)")

print(f"\n📊 MODEL QUALITY METRICS:")
print(f"  Variance Explained: {explained_var:.2%}")
if all_recs:
    avg_score = pd.DataFrame(all_recs)['cf_score'].mean()
    print(f"  Avg Recommendation Score: {avg_score:.3f}")
if all_item_recs:
    avg_sim = pd.DataFrame(all_item_recs)['similarity_score'].mean()
    print(f"  Avg Item Similarity: {avg_sim:.3f}")

print(f"\n💡 NEXT STEPS:")
print(f"  1. Check the metrics above")
print(f"  2. Adjust hyperparameters at the top of this script")
print(f"  3. Run again to compare")
print(f"  4. When satisfied with metrics:")
print(f"     - Copy best hyperparameters to cf_train_simple.py")
print(f"     - Set DATA_SAMPLE_PERCENT = 100 for production")
print(f"     - Run: python ml/recommenders/cf_train_simple.py")

print(f"\n🎯 HYPERPARAMETER TUNING GUIDE:")
print(f"  Higher N_COMPONENTS = Better quality, slower training")
print(f"    Recommended: 50 (good balance)")
print(f"  More SVD_ITERATIONS = Better convergence, slower")
print(f"    Recommended: 50-100")
print(f"  More SIMILAR_USERS = More diverse recommendations")
print(f"    Recommended: 20 (default)")
print(f"  More SIMILAR_ITEMS = More similar product suggestions")
print(f"    Recommended: 20 (default)")

print("\n" + "="*80 + "\n")
