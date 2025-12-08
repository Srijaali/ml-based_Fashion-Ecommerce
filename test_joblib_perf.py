import joblib
import time
from pathlib import Path

bundle_path = Path('data/recommendations/cf_models_bundle.joblib')

print(f'Bundle size: {bundle_path.stat().st_size / (1024*1024):.1f} MB\n')

# Test load time
start = time.time()
bundle = joblib.load(str(bundle_path))
elapsed = time.time() - start

print(f'Joblib load time: {elapsed:.2f}s')
print(f'Bundle keys: {list(bundle.keys())}')

print(f'\nBreakdown:')
print(f'  Recommendations: {len(bundle["recs_df"])} rows')
print(f'  User factors: {bundle["user_factors"].shape}')
print(f'  Item factors: {bundle["item_factors"].shape}')
print(f'  Item similarity: {bundle["item_similarity"]}')

# Compare with individual file loading
print(f'\n--- COMPARISON: Individual File Loading ---\n')

import pandas as pd
import numpy as np
import pickle

start = time.time()
recs_df = pd.read_csv('data/recommendations/recommendations.csv')
user_factors = np.load('data/recommendations/user_latent_factors.npy')
item_factors = np.load('data/recommendations/item_latent_factors.npy')
with open('data/recommendations/customer_mapping.pkl', 'rb') as f:
    customer_mapping = pickle.load(f)
with open('data/recommendations/item_mapping.pkl', 'rb') as f:
    item_mapping = pickle.load(f)
elapsed_individual = time.time() - start

print(f'Individual file load time: {elapsed_individual:.2f}s')

print(f'\n=== PERFORMANCE ===')
print(f'Joblib bundle: {elapsed:.2f}s')
print(f'Individual files: {elapsed_individual:.2f}s')
if elapsed < elapsed_individual:
    improvement = ((elapsed_individual - elapsed) / elapsed_individual) * 100
    print(f'✓ Joblib is {improvement:.0f}% FASTER')
else:
    print(f'⚠ Individual files slightly faster (acceptable for large arrays)')
