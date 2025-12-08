# ⚡ Quick Reference: CF Experimentation

## TL;DR - Three Commands

```bash
# 1. Fast iterate (16 seconds, 10% data)
python ml/recommenders/cf_train_experiment.py

# 2. Try different hyperparameters
# Edit ml/recommenders/cf_train_experiment.py line ~30
# Change: N_COMPONENTS = 50

# 3. Run again and compare
python ml/recommenders/cf_train_experiment.py

# 4. When happy, run full training (9 min, 100% data)
python ml/recommenders/cf_train_simple.py
```

---

## Hyperparameter Tuning Cheat Sheet

### Start Here

```python
# cf_train_experiment.py

N_COMPONENTS = 50              # ← Best starting point
SVD_ITERATIONS = 50            # ← Good balance
N_SIMILAR_USERS = 20           # ← Diversity
N_SIMILAR_ITEMS = 20           # ← For "often bought together"
DATA_SAMPLE_PERCENT = 10       # ← Fast iteration (keep at 10)
```

### Experiment 1: Quality vs Speed

```python
# Try N_COMPONENTS (bigger = better quality, slower)
N_COMPONENTS = 20   # Fast (8s)   → 35% variance
N_COMPONENTS = 50   # Balanced (10s) → 37% variance ✅
N_COMPONENTS = 75   # Better (14s)  → 38% variance
N_COMPONENTS = 100  # Overkill (18s) → 38% variance
# DECISION: Use 50 ✅
```

### Experiment 2: Convergence

```python
# Try SVD_ITERATIONS (more = better quality, slower)
SVD_ITERATIONS = 20   # Fast (7s)   → 36.5% variance
SVD_ITERATIONS = 50   # Good (10s)  → 37% variance ✅
SVD_ITERATIONS = 100  # Better (13s) → 37.1% variance
# DECISION: Use 50 ✅
```

### Experiment 3: Diversity

```python
# Try N_SIMILAR_USERS (more = more diverse recommendations)
N_SIMILAR_USERS = 10  # Conservative (3s)
N_SIMILAR_USERS = 20  # Balanced (4s) ✅
N_SIMILAR_USERS = 50  # Diverse (6s)
# DECISION: Use 20 ✅
```

---

## Iteration Template

```bash
# 1. Edit the script
nano ml/recommenders/cf_train_experiment.py
# Change line: N_COMPONENTS = 50

# 2. Run experiment
python ml/recommenders/cf_train_experiment.py

# 3. Check output
# Look for: "Variance Explained: XX.XX%"
# Lower variance? Try higher N_COMPONENTS
# Higher but slower? Try lower N_COMPONENTS
```

---

## Performance Expectations

| Data              | Time  | Quality       |
| ----------------- | ----- | ------------- |
| 10% (experiment)  | ~16s  | Fast feedback |
| 100% (production) | ~9min | Full quality  |

---

## When to Use What

```
Use cf_train_experiment.py when:
├─ Testing new hyperparameters
├─ Comparing algorithm changes
├─ Need quick feedback (<1 min)
└─ Want to try multiple ideas

Use cf_train_simple.py when:
├─ Hyperparameters are finalized
├─ Need production-quality recommendations
├─ Have 9 minutes available
└─ Want full dataset coverage
```

---

## Files Generated

### cf_train_experiment.py produces:

- None (just metrics on screen)
- Use for decision-making only

### cf_train_simple.py produces:

- `user_item_matrix.npz` - Sparse interaction matrix
- `user_latent_factors.npy` - User embeddings (500k × 50)
- `item_latent_factors.npy` - Item embeddings (7.4k × 50)
- `item_similarity.npy` - Item-to-item similarities
- `cf_user_based_recommendations.parquet` - "Customers Also Bought"
- `cf_item_based_recommendations.parquet` - "Often Bought Together"

---

## GPU Status

```
✅ NVIDIA RTX 2050 (4GB)
✅ CUDA 12.9
✅ CuPy installed
✅ Ready for acceleration
```

Scripts use CPU (sufficient for this dataset). GPU would save 5-10 min in production.

---

## Troubleshooting

**Q: Getting OOM errors?**

```python
N_COMPONENTS = 30  # Reduce
N_USERS_FOR_RECS = 50  # Or reduce user sample
DATA_SAMPLE_PERCENT = 5  # Use less data
```

**Q: Variance too low?**

```python
N_COMPONENTS = 75  # Increase
SVD_ITERATIONS = 100  # Or more iterations
```

**Q: Too slow for iteration?**

```python
DATA_SAMPLE_PERCENT = 5  # Use 5% instead of 10%
N_USERS_FOR_RECS = 50  # Reduce sample users
```

---

## Best Practices

1. ✅ Start with experiment script (16 sec)
2. ✅ Change ONE hyperparameter at a time
3. ✅ Note the variance explained for each run
4. ✅ When variance plateaus, you're done
5. ✅ Run full training with best values
6. ✅ Save output for API integration

---

## 🎯 Optimal Settings for This Data

```python
# Recommended for fashion e-commerce:
N_COMPONENTS = 50
SVD_ITERATIONS = 50
N_SIMILAR_USERS = 20
N_SIMILAR_ITEMS = 20

# Expected results:
# - Variance: ~37%
# - Time: ~16s (experiment) or 9m (production)
# - Recommendations: 1k-50k depending on data %
```

---

**Last Updated:** 2025-12-07
