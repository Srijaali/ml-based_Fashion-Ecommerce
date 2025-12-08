"""
Rapid Testing Suite for Collaborative Filtering
Combines fast iteration + evaluation for quick feedback loop

🚀 USAGE:
   python test_cf_rapid.py --components=50 --iterations=50 --verbose

⏱️  TIME: ~35 seconds per iteration
   • Experiment (10% data): 17 sec
   • Evaluation: 15 sec
   • Total: 32-35 sec

📊 OUTPUT:
   • Variance explained
   • Coverage %
   • Diversity (items per user)
   • Novelty (% new items)
   • Quality score /100
   • Recommended next hyperparameters

🔄 WORKFLOW:
   1. Run this script
   2. Check metrics
   3. If not satisfied, modify hyperparameters in cf_train_experiment.py
   4. Run again (35 sec)
   5. Iterate until happy (usually 5-10 iterations)
   6. When satisfied, train on Kaggle GPU
"""

import os
import sys
import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# ============================================================================
# SETUP
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
RECOMMENDERS_DIR = PROJECT_ROOT / 'ml' / 'recommenders'

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    def __init__(self, components=50, iterations=50, verbose=False):
        self.n_components = components
        self.svd_iterations = iterations
        self.verbose = verbose
        self.experiment_script = RECOMMENDERS_DIR / 'cf_train_experiment.py'
        self.evaluate_script = RECOMMENDERS_DIR / 'cf_evaluate.py'

# ============================================================================
# STEP 1: RUN EXPERIMENT
# ============================================================================

def run_experiment(config):
    """Run fast iteration experiment"""
    print("\n" + "=" * 80)
    print("STEP 1: FAST EXPERIMENT (10% data, ~17 seconds)")
    print("=" * 80 + "\n")
    
    cmd = [
        sys.executable,
        str(config.experiment_script),
        f"--components={config.n_components}",
        f"--iterations={config.svd_iterations}"
    ]
    
    if config.verbose:
        cmd.append("--verbose")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(RECOMMENDERS_DIR),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print("❌ Experiment failed!")
            print(result.stderr)
            return False
        
        # Extract metrics from output
        output = result.stdout
        print(output)
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Experiment timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running experiment: {e}")
        return False

# ============================================================================
# STEP 2: RUN EVALUATION
# ============================================================================

def run_evaluation(config):
    """Run model evaluation"""
    print("\n" + "=" * 80)
    print("STEP 2: EVALUATE MODEL (all 7 metrics, ~15 seconds)")
    print("=" * 80 + "\n")
    
    cmd = [sys.executable, str(config.evaluate_script)]
    
    if config.verbose:
        cmd.append("--verbose")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(RECOMMENDERS_DIR),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print("❌ Evaluation failed!")
            print(result.stderr)
            return False
        
        output = result.stdout
        print(output)
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Evaluation timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running evaluation: {e}")
        return False

# ============================================================================
# STEP 3: SUMMARY & RECOMMENDATIONS
# ============================================================================

def print_recommendations(config):
    """Print next steps"""
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80 + "\n")
    
    print("""
✅ IF QUALITY SCORE ≥ 75 / 100:
   
   Great! Your model is ready for production. Next steps:
   
   1. Train on Kaggle GPU (400k users):
      • Open Kaggle Notebook
      • Paste cf_train_kaggle.py
      • Select GPU (right sidebar)
      • Run (15-20 minutes)
   
   2. Download results:
      • user_based_recommendations.parquet
      • item_based_recommendations.parquet
      • All embeddings & mappings
   
   3. Copy to data/recommendations/
   
   4. Create FastAPI endpoints using the recommendations

⚠️  IF QUALITY SCORE < 75 / 100:
   
   Iterate on hyperparameters:
   
   1. Edit cf_train_experiment.py (top of file):
      
      # Try different values:
      N_COMPONENTS = 50       # Try: 30, 40, 50, 60, 100
      SVD_ITERATIONS = 50     # Try: 30, 50, 100, 200
      MIN_SIMILARITY = 0.1    # Try: 0.05, 0.1, 0.2
   
   2. Run this script again:
      python test_cf_rapid.py --components=50 --iterations=50
   
   3. Check results (35 sec per iteration)
   
   4. Repeat 2-3 more times (usually converges in 5-10 iterations)

💡 TUNING GUIDE:

   If Coverage is low (< 50%):
      → Decrease N_COMPONENTS (30-40)
      → Decrease MIN_SIMILARITY (0.05)
      → Increase SVD_ITERATIONS (100-200)
   
   If Variance is low (< 30%):
      → Increase N_COMPONENTS (60-100)
      → Increase SVD_ITERATIONS (100-200)
   
   If Personalization is low (< 30%):
      → Increase N_COMPONENTS (80-100)
      → Decrease KNN_NEIGHBORS (10-15)
   
   If Diversity is low (< 15 items/user):
      → Decrease N_COMPONENTS (30-40)
      → Increase MIN_SIMILARITY (0.15-0.2)

📊 BENCHMARK TARGETS:

   Component              Target      Current Status
   ─────────────────────────────────────────────────
   Coverage               > 80%       ⚠️  (depends on users)
   Variance Explained     > 40%       ⚠️  (depends on components)
   Diversity              > 15/20     ⚠️  (depends on sampling)
   Novelty                > 90%       ✅ (usually good)
   Quality Score          > 75/100    ⚠️  (check output above)
   Personalization        > 30%       ⚠️  (depends on components)

🎯 PRODUCTION READINESS:

   ✅ Ready if:
      • Quality Score ≥ 75
      • Coverage ≥ 50%
      • Variance ≥ 35%
      • Diversity ≥ 10
   
   ⏳ Needs tuning if:
      • Any metric below target
      • Quality score < 75

📝 LOG YOUR RESULTS:

   Iteration | Components | Iterations | Score | Coverage | Variance | Notes
   ──────────────────────────────────────────────────────────────────────────
   1         | 50         | 50         | ?     | ?%       | ?%       |
   2         | ?          | ?          | ?     | ?%       | ?%       |
   3         | ?          | ?          | ?     | ?%       | ?%       |

""")

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Rapid testing suite for Collaborative Filtering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_cf_rapid.py                              # Use defaults (50, 50)
  python test_cf_rapid.py --components=100 --iterations=100
  python test_cf_rapid.py --components=30 --iterations=30 --verbose
        """
    )
    
    parser.add_argument('--components', type=int, default=50,
                       help='Number of SVD components (default: 50)')
    parser.add_argument('--iterations', type=int, default=50,
                       help='SVD iterations (default: 50)')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    config = Config(
        components=args.components,
        iterations=args.iterations,
        verbose=args.verbose
    )
    
    print("\n" + "=" * 80)
    print("COLLABORATIVE FILTERING - RAPID TESTING SUITE")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  N_COMPONENTS: {config.n_components}")
    print(f"  SVD_ITERATIONS: {config.svd_iterations}")
    print(f"  Verbose: {config.verbose}")
    print(f"\nExpected time: ~35 seconds total\n")
    
    start_time = datetime.now()
    
    # Step 1: Experiment
    if not run_experiment(config):
        print("\n❌ Testing failed at experiment step")
        return False
    
    # Step 2: Evaluation
    if not run_evaluation(config):
        print("\n❌ Testing failed at evaluation step")
        return False
    
    # Step 3: Recommendations
    print_recommendations(config)
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print("=" * 80)
    print(f"✅ TESTING COMPLETE")
    print(f"   Total time: {elapsed:.1f} seconds")
    print("=" * 80 + "\n")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
