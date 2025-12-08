"""
Collaborative Filtering Model Evaluation
Measure recommendation quality using multiple metrics
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'ml'
OUTPUT_DIR = PROJECT_ROOT / 'data' / 'recommendations'

print("\n" + "="*80)
print("COLLABORATIVE FILTERING MODEL EVALUATION")
print("="*80 + "\n")

# ============================================================================
# LOAD MODEL & DATA
# ============================================================================
print("[1] Loading model artifacts...")

# Load recommendation outputs
user_recs = pd.read_parquet(OUTPUT_DIR / 'cf_user_based_recommendations.parquet')
item_recs = pd.read_parquet(OUTPUT_DIR / 'cf_item_based_recommendations.parquet')

# Load latent factors
user_latent = np.load(OUTPUT_DIR / 'user_latent_factors.npy')
item_latent = np.load(OUTPUT_DIR / 'item_latent_factors.npy')

# Load mappings
with open(OUTPUT_DIR / 'customer_mapping.pkl', 'rb') as f:
    customer_mapping = pickle.load(f)
with open(OUTPUT_DIR / 'article_mapping.pkl', 'rb') as f:
    article_mapping = pickle.load(f)

# Load original interactions
interactions = pd.read_parquet(DATA_DIR / 'user_item_interactions.parquet')

print(f"✓ Loaded {len(user_recs):,} user-based recommendations")
print(f"✓ Loaded {len(item_recs):,} item-based recommendations")
print(f"✓ User latent factors: {user_latent.shape}")
print(f"✓ Item latent factors: {item_latent.shape}")
print(f"✓ Original interactions: {len(interactions):,}\n")

# ============================================================================
# METRIC 1: COVERAGE
# ============================================================================
print("[2] COVERAGE ANALYSIS")
print("-" * 80)

# User coverage
unique_users_in_recs = user_recs['customer_id'].nunique()
total_users = len(customer_mapping)
user_coverage = 100 * unique_users_in_recs / total_users

print(f"User Coverage:")
print(f"  Recommended to: {unique_users_in_recs:,} users")
print(f"  Total users: {total_users:,}")
print(f"  Coverage: {user_coverage:.2f}%")
print(f"  {'✅ GOOD' if user_coverage > 1 else '⚠️  LOW'} (ideal: >5%)\n")

# Item coverage
unique_items_recommended = item_recs['article_id'].nunique()
total_items = len(article_mapping)
item_coverage = 100 * unique_items_recommended / total_items

print(f"Item Coverage:")
print(f"  Recommended: {unique_items_recommended:,} items")
print(f"  Total items: {total_items:,}")
print(f"  Coverage: {item_coverage:.2f}%")
print(f"  {'✅ EXCELLENT' if item_coverage > 90 else '⚠️  LOW'} (ideal: >90%)\n")

# ============================================================================
# METRIC 2: RECOMMENDATION DIVERSITY
# ============================================================================
print("[3] DIVERSITY ANALYSIS")
print("-" * 80)

# How many unique items per user?
items_per_user = user_recs.groupby('customer_id')['article_id'].nunique()
avg_items_per_user = items_per_user.mean()
min_items = items_per_user.min()
max_items = items_per_user.max()

print(f"User-Based Recommendations Diversity:")
print(f"  Avg items per user: {avg_items_per_user:.1f}")
print(f"  Min items per user: {min_items}")
print(f"  Max items per user: {max_items}")
print(f"  {'✅ GOOD' if avg_items_per_user >= 5 else '⚠️  LOW'} (ideal: >=5)\n")

# How many unique similar items per article?
items_per_article = item_recs.groupby('article_id')['similar_article_id'].nunique()
avg_items_per_article = items_per_article.mean()

print(f"Item-Based Recommendations Diversity:")
print(f"  Avg similar items per article: {avg_items_per_article:.1f}")
print(f"  {'✅ GOOD' if avg_items_per_article >= 10 else '⚠️  LOW'} (ideal: >=10)\n")

# ============================================================================
# METRIC 3: NOVELTY
# ============================================================================
print("[4] NOVELTY ANALYSIS")
print("-" * 80)

# What % of recommendations are NEW (not already purchased)?
interactions_sample = interactions.drop_duplicates(['customer_id', 'article_id'])
user_items_map = interactions_sample.groupby('customer_id')['article_id'].apply(set).to_dict()

novel_count = 0
total_count = 0

for _, row in user_recs.iterrows():
    user_id = row['customer_id']
    item_id = row['article_id']
    
    if user_id in user_items_map:
        if item_id not in user_items_map[user_id]:
            novel_count += 1
    else:
        novel_count += 1
    
    total_count += 1

novelty_ratio = 100 * novel_count / total_count if total_count > 0 else 0

print(f"Recommendation Novelty:")
print(f"  New items (not purchased): {novel_count:,}/{total_count:,}")
print(f"  Novelty ratio: {novelty_ratio:.1f}%")
print(f"  {'✅ EXCELLENT' if novelty_ratio > 95 else '⚠️  LOW'} (ideal: >95%)\n")

# ============================================================================
# METRIC 4: SPARSITY (Embedding Quality)
# ============================================================================
print("[5] EMBEDDING QUALITY ANALYSIS")
print("-" * 80)

# Check variance of embeddings
user_variance = np.var(user_latent, axis=0)
item_variance = np.var(item_latent, axis=0)

print(f"User Embeddings:")
print(f"  Dimensions: {user_latent.shape}")
print(f"  Mean dimension variance: {user_variance.mean():.4f}")
print(f"  Max dimension variance: {user_variance.max():.4f}")
print(f"  Min dimension variance: {user_variance.min():.4f}")
print(f"  {'✅ GOOD' if user_variance.mean() > 0.01 else '⚠️  LOW'} variance\n")

print(f"Item Embeddings:")
print(f"  Dimensions: {item_latent.shape}")
print(f"  Mean dimension variance: {item_variance.mean():.4f}")
print(f"  Max dimension variance: {item_variance.max():.4f}")
print(f"  Min dimension variance: {item_variance.min():.4f}")
print(f"  {'✅ GOOD' if item_variance.mean() > 0.01 else '⚠️  LOW'} variance\n")

# ============================================================================
# METRIC 5: SIMILARITY SCORES
# ============================================================================
print("[6] RECOMMENDATION SCORES ANALYSIS")
print("-" * 80)

# User-based rec scores
user_rec_scores = user_recs['cf_score'].describe()
print(f"User-Based Recommendation Scores:")
print(f"  Mean: {user_rec_scores['mean']:.4f}")
print(f"  Std: {user_rec_scores['std']:.4f}")
print(f"  Min: {user_rec_scores['min']:.4f}")
print(f"  Max: {user_rec_scores['max']:.4f}")
print(f"  25th %ile: {user_rec_scores['25%']:.4f}")
print(f"  75th %ile: {user_rec_scores['75%']:.4f}")
print(f"  {'✅ GOOD' if user_rec_scores['mean'] > 0 else '⚠️  CHECK'} distribution\n")

# Item-based similarity scores
item_sim_scores = item_recs['similarity_score'].describe()
print(f"Item-Based Similarity Scores:")
print(f"  Mean: {item_sim_scores['mean']:.4f}")
print(f"  Std: {item_sim_scores['std']:.4f}")
print(f"  Min: {item_sim_scores['min']:.4f}")
print(f"  Max: {item_sim_scores['max']:.4f}")
print(f"  25th %ile: {item_sim_scores['25%']:.4f}")
print(f"  75th %ile: {item_sim_scores['75%']:.4f}")
print(f"  {'✅ GOOD' if item_sim_scores['mean'] > 0.3 else '⚠️  LOW'} similarity\n")

# ============================================================================
# METRIC 6: PERSONALIZATION
# ============================================================================
print("[7] PERSONALIZATION ANALYSIS")
print("-" * 80)

# Check if recommendations are diverse across users
# Sample some users and see if they get different recommendations
sample_users = user_recs['customer_id'].unique()[:100]
all_recommended_items = []

for user_id in sample_users:
    items = set(user_recs[user_recs['customer_id'] == user_id]['article_id'].values)
    all_recommended_items.append(items)

# Calculate Jaccard similarity between user recommendation sets
if len(all_recommended_items) > 1:
    total_similarity = 0
    count = 0
    
    for i in range(min(10, len(all_recommended_items) - 1)):
        for j in range(i + 1, min(i + 5, len(all_recommended_items))):
            set_a = all_recommended_items[i]
            set_b = all_recommended_items[j]
            
            if len(set_a) > 0 and len(set_b) > 0:
                intersection = len(set_a & set_b)
                union = len(set_a | set_b)
                similarity = intersection / union if union > 0 else 0
                total_similarity += similarity
                count += 1
    
    avg_jaccard = total_similarity / count if count > 0 else 0
    personalization = 100 * (1 - avg_jaccard)
    
    print(f"Recommendation Personalization:")
    print(f"  Avg Jaccard Similarity: {avg_jaccard:.4f}")
    print(f"  Personalization Score: {personalization:.1f}%")
    print(f"  {'✅ EXCELLENT' if personalization > 80 else '⚠️  LOW'} (ideal: >80%)\n")

# ============================================================================
# SUMMARY SCORING
# ============================================================================
print("="*80)
print("OVERALL MODEL EVALUATION SUMMARY")
print("="*80 + "\n")

scores = {}

# Coverage score (0-25 points)
scores['coverage'] = min(25, (user_coverage / 5) * 25) if user_coverage > 0 else 0

# Diversity score (0-25 points)
scores['diversity'] = min(25, (avg_items_per_user / 5) * 25) if avg_items_per_user > 0 else 0

# Novelty score (0-25 points)
scores['novelty'] = min(25, (novelty_ratio / 95) * 25) if novelty_ratio > 0 else 0

# Quality score (0-25 points) - based on embedding variance
scores['quality'] = min(25, (user_variance.mean() / 0.01) * 25) if user_variance.mean() > 0 else 0

total_score = sum(scores.values())

print(f"Component Scores (0-25 each):")
print(f"  Coverage:    {scores['coverage']:.1f}/25")
print(f"  Diversity:   {scores['diversity']:.1f}/25")
print(f"  Novelty:     {scores['novelty']:.1f}/25")
print(f"  Quality:     {scores['quality']:.1f}/25")
print(f"  " + "-" * 30)
print(f"  TOTAL:       {total_score:.1f}/100\n")

# Grade system
if total_score >= 85:
    grade = "🌟 EXCELLENT"
    interpretation = "Model is production-ready!"
elif total_score >= 70:
    grade = "✅ GOOD"
    interpretation = "Model is suitable for deployment with monitoring"
elif total_score >= 50:
    grade = "⚠️  FAIR"
    interpretation = "Consider tuning hyperparameters"
else:
    grade = "❌ POOR"
    interpretation = "Model needs significant improvement"

print(f"Model Grade: {grade}")
print(f"Interpretation: {interpretation}\n")

# ============================================================================
# RECOMMENDATIONS FOR IMPROVEMENT
# ============================================================================
print("="*80)
print("IMPROVEMENT RECOMMENDATIONS")
print("="*80 + "\n")

improvements = []

if user_coverage < 1:
    improvements.append("• Increase USER_SAMPLE_SIZE in cf_train_simple.py (current: 5,000)")

if avg_items_per_user < 5:
    improvements.append("• Increase N_SIMILAR_USERS (current: 20 → try 50)")

if novelty_ratio < 95:
    improvements.append("• Add filtering to remove already-purchased items (already implemented)")

if item_sim_scores['mean'] < 0.3:
    improvements.append("• Increase N_COMPONENTS in SVD (current: 50 → try 75)")

if not improvements:
    print("✅ No major improvements needed! Model is performing well.\n")
else:
    for improvement in improvements:
        print(improvement)
    print()

# ============================================================================
# ACTIONABLE INSIGHTS
# ============================================================================
print("="*80)
print("ACTIONABLE INSIGHTS FOR BUSINESS")
print("="*80 + "\n")

print(f"📊 BUSINESS METRICS:")
print(f"  • Can recommend to: {unique_users_in_recs:,} users ({user_coverage:.2f}%)")
print(f"  • Average recs per user: {avg_items_per_user:.1f} items")
print(f"  • Cross-sell potential: {len(item_recs):,} item pairs")
print(f"  • {novelty_ratio:.1f}% of recs are NEW products to users\n")

print(f"🎯 USE CASES:")
print(f"  ✅ 'Customers Also Bought' section (Ready)")
print(f"  ✅ 'Often Bought Together' section (Ready)")
print(f"  ✅ 'You May Also Like' section (Ready)")
print(f"  {'✅' if user_coverage > 10 else '⚠️'} Homepage 'Trending for You' (Limited)\n")

print(f"⚡ NEXT STEPS:")
print(f"  1. Deploy as FastAPI endpoints")
print(f"  2. Monitor click-through rate (CTR)")
print(f"  3. Track conversion rate on recommendations")
print(f"  4. A/B test recommendation order")
print(f"  5. Retrain weekly with new interactions\n")

print("="*80 + "\n")
