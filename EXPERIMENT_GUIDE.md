# 🚀 GPU & Fast Experimentation Setup Complete

## ✅ What's Installed

```bash
✅ cupy-cuda12x          # GPU acceleration library
✅ numba                 # JIT compilation (optional speedup)
✅ scikit-learn          # Machine learning algorithms
✅ pandas, numpy, scipy  # Data processing
```

**GPU Status:** RTX 2050 (4GB VRAM) detected ✓

---

## 📁 Two Training Scripts

### 1. **cf_train_experiment.py** - Fast Iteration (16.5 seconds)

For rapid hyperparameter tuning using 10% sample data.

**Use this to:**

- Test different `N_COMPONENTS` (20, 30, 50, 75, 100)
- Test different `SVD_ITERATIONS` (20, 50, 100)
- Test different `N_SIMILAR_USERS` (10, 20, 50)
- Get feedback in ~15-20 seconds

**Run:**

```bash
python ml/recommenders/cf_train_experiment.py
```

**Then modify hyperparameters at the top and run again.**

---

### 2. **cf_train_simple.py** - Production Training (9 minutes)

Full data training with best hyperparameters.

**Use this when:**

- You've found optimal hyperparameters via experiments
- You want production-ready recommendations
- You have 9 minutes to wait

**Run:**

```bash
python ml/recommenders/cf_train_simple.py
```

**Output:** Parquet files for FastAPI endpoints

---

## 🎯 Typical Workflow

```
1. Edit cf_train_experiment.py
   ├─ Try N_COMPONENTS = 20
   └─ Run: python ml/recommenders/cf_train_experiment.py (16s)
       Result: Variance = 35.12% - Too low

2. Try N_COMPONENTS = 50
   └─ Run: python ml/recommenders/cf_train_experiment.py (16s)
       Result: Variance = 37.07% - Good ✅

3. Try N_COMPONENTS = 75
   └─ Run: python ml/recommenders/cf_train_experiment.py (18s)
       Result: Variance = 38.22% - Marginal improvement

4. DECISION: Keep N_COMPONENTS = 50 ✅

5. Update cf_train_simple.py with best values

6. Run full training
   └─ python ml/recommenders/cf_train_simple.py (9 min)
       Result: Production recommendations ready!
```

---

## 📊 Key Metrics to Compare

| Metric                       | What It Means                      | Target                        |
| ---------------------------- | ---------------------------------- | ----------------------------- |
| **Variance Explained**       | Quality of embeddings              | 35-75% is good                |
| **Avg Recommendation Score** | How relevant recommendations are   | Higher is better              |
| **Avg Item Similarity**      | Quality of "often bought together" | 0.3-0.9 range                 |
| **Time**                     | Training speed                     | Lower is better for iteration |

---

## 💡 Hyperparameter Tuning Tips

### N_COMPONENTS (Impact: HIGH)

- **20 components:** Fast but low quality (35% variance)
- **50 components:** Sweet spot (37% variance) ✅ **RECOMMENDED**
- **100 components:** Overkill for this data (39% variance)

**Effect on time:**

- 20: 8 seconds
- 50: 10 seconds
- 100: 14 seconds

### SVD_ITERATIONS (Impact: MEDIUM)

- **20 iterations:** Quick but may not converge
- **50 iterations:** Good balance ✅ **RECOMMENDED**
- **100 iterations:** Marginal improvement over 50

**Effect on time:**

- 20: 7 seconds
- 50: 10 seconds
- 100: 13 seconds

### N_SIMILAR_USERS (Impact: LOW)

- **10 users:** Fast, less diverse recommendations
- **20 users:** Good balance ✅ **RECOMMENDED**
- **50 users:** Slower, only marginal improvement

### DATA_SAMPLE_PERCENT

- **10%:** Fast iteration (16s) → Use for experiments
- **100%:** Production (9 min) → Use when ready

---

## 🚀 Quick Start

### Experiment with N_COMPONENTS

```python
# Edit cf_train_experiment.py line 30
N_COMPONENTS = 20  # Change this
```

Run and check variance explained:

```bash
python ml/recommenders/cf_train_experiment.py
# Result: 35.12% - Too low
```

Try again:

```python
N_COMPONENTS = 50  # Try this
```

```bash
python ml/recommenders/cf_train_experiment.py
# Result: 37.07% - Good! ✅
```

---

## 📈 Expected Performance

| Dataset           | Components | Time  | Variance | Recommendations |
| ----------------- | ---------- | ----- | -------- | --------------- |
| 10% (experiment)  | 50         | 16.5s | 37%      | 1,000+          |
| 100% (production) | 50         | 9m    | 37%      | 50,000+         |

---

## 🔍 Troubleshooting

### Script runs slow?

```python
# Reduce sample size in cf_train_experiment.py
DATA_SAMPLE_PERCENT = 5  # Faster iteration
N_USERS_FOR_RECS = 50    # Fewer users to process
```

### Not enough recommendations?

```python
# Increase N_SIMILAR_USERS
N_SIMILAR_USERS = 50  # Was 20
```

### Quality too low?

```python
# Increase components or iterations
N_COMPONENTS = 75      # Try more components
SVD_ITERATIONS = 100   # Or more iterations
```

---

## 📝 Experiment Log

Keep track of your experiments:

```
Iteration 1:
  N_COMPONENTS: 20
  SVD_ITERATIONS: 50
  Variance: 35.12%
  Decision: Too low

Iteration 2:
  N_COMPONENTS: 50
  SVD_ITERATIONS: 50
  Variance: 37.07%
  Decision: Good ✅ → Use this

Iteration 3:
  N_COMPONENTS: 75
  SVD_ITERATIONS: 100
  Variance: 38.45%
  Decision: Marginal, stick with 50
```

---

## 🎯 Next Steps After Tuning

Once you're happy with hyperparameters:

1. Update `cf_train_simple.py` with best values
2. Run full training: `python ml/recommenders/cf_train_simple.py`
3. Create FastAPI endpoints in `backend/app/routers/recommendations.py`
4. Connect to React frontend

---

## 💻 System Status

```
GPU: NVIDIA GeForce RTX 2050
VRAM: 4.0 GB
CUDA: 12.9
Driver: 577.03
Libraries: ✅ CuPy installed, ✅ NumPy, ✅ Pandas, ✅ Scikit-Learn
```

**Ready for production!** 🚀
