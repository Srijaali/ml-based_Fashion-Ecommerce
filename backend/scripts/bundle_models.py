#!/usr/bin/env python
"""
Bundle existing model artifacts into joblib files for faster loading.

This script:
1. Loads all individual CF artifacts (.npy, .pkl, .csv)
2. Bundles them into a single cf_models_bundle.joblib file
3. Optionally does the same for CB models (once downloaded from Kaggle)
4. Validates bundles before saving
5. Can be run multiple times (overwrites existing bundles)

Usage:
    python backend/scripts/bundle_models.py                     # Bundle CF + CB
    python backend/scripts/bundle_models.py --cf-only           # Bundle CF only
    python backend/scripts/bundle_models.py --no-compress       # No compression
    python backend/scripts/bundle_models.py --verify            # Just verify bundles
"""

import argparse
import sys
import logging
from pathlib import Path

# Add parent directories to path for imports
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
project_dir = backend_dir.parent
sys.path.insert(0, str(backend_dir))

import numpy as np
import pandas as pd
import pickle

from app.services.model_persistence import ModelPersistence

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ModelBundler:
    """Bundle individual model artifacts into joblib files"""

    def __init__(self, cf_dir: str, cb_dir: str, output_dir: str):
        """
        Initialize bundler.

        Args:
            cf_dir: Path to CF artifacts directory
            cb_dir: Path to CB artifacts directory
            output_dir: Path to save bundle files
        """
        self.cf_dir = Path(cf_dir)
        self.cb_dir = Path(cb_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def bundle_cf_models(self, compress: bool = False) -> bool:
        """
        Bundle CF models from individual files.

        Args:
            compress: Whether to compress the bundle

        Returns:
            bool: Success status
        """
        print("\n" + "="*70)
        print("BUNDLING CF MODELS")
        print("="*70)

        try:
            # Check for required files
            recs_file = self.cf_dir / "recommendations.csv"
            user_factors_file = self.cf_dir / "user_latent_factors.npy"
            item_factors_file = self.cf_dir / "item_latent_factors.npy"
            customer_map_file = self.cf_dir / "customer_mapping.pkl"
            item_map_file = self.cf_dir / "item_mapping.pkl"

            # Optional: item_similarity (not always present)
            item_sim_file = self.cf_dir / "item_similarity.npy"

            required_files = [
                recs_file,
                user_factors_file,
                item_factors_file,
                customer_map_file,
                item_map_file,
            ]

            missing = [f for f in required_files if not f.exists()]
            if missing:
                logger.error(f"✗ Missing CF files:")
                for f in missing:
                    logger.error(f"  - {f}")
                return False

            logger.info("✓ All required CF files found, loading...")

            # Load recommendations
            logger.info(f"  Loading recommendations.csv...")
            recs_df = pd.read_csv(recs_file)
            logger.info(f"    → {len(recs_df):,} recommendations loaded")

            # Load latent factors
            logger.info(f"  Loading user_latent_factors.npy...")
            user_factors = np.load(user_factors_file)
            logger.info(f"    → Shape: {user_factors.shape}")

            logger.info(f"  Loading item_latent_factors.npy...")
            item_factors = np.load(item_factors_file)
            logger.info(f"    → Shape: {item_factors.shape}")

            # Load similarity matrix (optional)
            item_similarity = None
            if item_sim_file.exists():
                logger.info(f"  Loading item_similarity.npy...")
                item_similarity = np.load(item_sim_file)
                logger.info(f"    → Shape: {item_similarity.shape}")
            else:
                logger.warning(f"  ⚠ item_similarity.npy not found (optional)")

            # Load mappings
            logger.info(f"  Loading customer_mapping.pkl...")
            with open(customer_map_file, "rb") as f:
                customer_mapping = pickle.load(f)
            logger.info(f"    → {len(customer_mapping):,} customer mappings")

            logger.info(f"  Loading item_mapping.pkl...")
            with open(item_map_file, "rb") as f:
                item_mapping = pickle.load(f)
            logger.info(f"    → {len(item_mapping):,} item mappings")

            # Save bundle
            output_file = self.output_dir / "cf_models_bundle.joblib"
            metadata = {"source": "bundled from individual files"}

            success, message = ModelPersistence.save_cf_bundle(
                output_path=str(output_file),
                recs_df=recs_df,
                user_factors=user_factors,
                item_factors=item_factors,
                item_similarity=item_similarity,
                customer_mapping=customer_mapping,
                item_mapping=item_mapping,
                compress=compress,
                metadata=metadata,
            )

            if success:
                print(f"\n{message}")
                return True
            else:
                logger.error(message)
                return False

        except Exception as e:
            logger.error(f"✗ Error bundling CF models: {str(e)}")
            return False

    def bundle_cb_models(self, compress: bool = False) -> bool:
        """
        Bundle CB models from individual files.

        Args:
            compress: Whether to compress the bundle

        Returns:
            bool: Success status
        """
        print("\n" + "="*70)
        print("BUNDLING CB MODELS")
        print("="*70)

        try:
            # Check for required files
            sim_file = self.cb_dir / "article_similarity_matrix.npy"
            emb_file = self.cb_dir / "article_text_embeddings.npy"
            tfidf_file = self.cb_dir / "tfidf_vectorizer.pkl"
            scaler_file = self.cb_dir / "price_scaler.pkl"
            id_idx_file = self.cb_dir / "article_id_to_idx.pkl"
            config_file = self.cb_dir / "config.pkl"

            required_files = [sim_file, emb_file, tfidf_file, scaler_file, id_idx_file]

            missing = [f for f in required_files if not f.exists()]
            if missing:
                logger.warning(f"⚠ CB bundle requires these files (not found):")
                for f in missing:
                    logger.warning(f"  - {f}")
                logger.warning(
                    "\nTo create CB bundle, download artifacts from Kaggle:"
                )
                logger.warning("  1. Run your Kaggle notebook to generate artifacts")
                logger.warning("  2. Extract to: data/content_based_model/")
                logger.warning("  3. Run this script again")
                return False

            logger.info("✓ All CB files found, loading...")

            # Load similarity matrix
            logger.info(f"  Loading article_similarity_matrix.npy...")
            article_similarity = np.load(sim_file)
            logger.info(f"    → Shape: {article_similarity.shape}")

            # Load embeddings
            logger.info(f"  Loading article_text_embeddings.npy...")
            article_embeddings = np.load(emb_file)
            logger.info(f"    → Shape: {article_embeddings.shape}")

            # Load vectorizers
            logger.info(f"  Loading tfidf_vectorizer.pkl...")
            with open(tfidf_file, "rb") as f:
                tfidf_vectorizer = pickle.load(f)
            logger.info(f"    → Loaded")

            logger.info(f"  Loading price_scaler.pkl...")
            with open(scaler_file, "rb") as f:
                price_scaler = pickle.load(f)
            logger.info(f"    → Loaded")

            # Load mappings
            logger.info(f"  Loading article_id_to_idx.pkl...")
            with open(id_idx_file, "rb") as f:
                article_id_to_idx = pickle.load(f)
            logger.info(f"    → {len(article_id_to_idx):,} article mappings")

            # Load config if exists
            config = {}
            if config_file.exists():
                logger.info(f"  Loading config.pkl...")
                with open(config_file, "rb") as f:
                    config = pickle.load(f)
                logger.info(f"    → Loaded")

            # Save bundle
            output_file = self.output_dir / "cb_models_bundle.joblib"
            metadata = {"source": "bundled from individual files"}

            success, message = ModelPersistence.save_cb_bundle(
                output_path=str(output_file),
                article_similarity=article_similarity,
                article_embeddings=article_embeddings,
                tfidf_vectorizer=tfidf_vectorizer,
                price_scaler=price_scaler,
                article_id_to_idx=article_id_to_idx,
                config=config,
                compress=compress,
                metadata=metadata,
            )

            if success:
                print(f"\n{message}")
                return True
            else:
                logger.error(message)
                return False

        except Exception as e:
            logger.error(f"✗ Error bundling CB models: {str(e)}")
            return False

    def verify_bundles(self) -> bool:
        """
        Verify existing bundles and display info.

        Returns:
            bool: All bundles valid
        """
        print("\n" + "="*70)
        print("VERIFYING BUNDLES")
        print("="*70)

        all_valid = True

        # Check CF bundle
        cf_bundle = self.output_dir / "cf_models_bundle.joblib"
        bundle, msg = ModelPersistence.load_cf_bundle(str(cf_bundle))

        if bundle:
            print(f"\n✓ CF Bundle: VALID")
            print(f"  Path: {cf_bundle}")
            metadata = bundle.get("metadata", {})
            print(f"  Created: {metadata.get('created', 'unknown')}")
            print(f"  Users: {metadata.get('n_users', 'unknown')}")
            print(f"  Items: {metadata.get('n_items', 'unknown')}")
            print(f"  Recommendations: {metadata.get('n_recommendations', 'unknown')}")
        else:
            print(f"\n✗ CF Bundle: NOT FOUND or INVALID")
            print(f"  {msg}")
            all_valid = False

        # Check CB bundle
        cb_bundle = self.output_dir / "cb_models_bundle.joblib"
        bundle, msg = ModelPersistence.load_cb_bundle(str(cb_bundle))

        if bundle:
            print(f"\n✓ CB Bundle: VALID")
            print(f"  Path: {cb_bundle}")
            metadata = bundle.get("metadata", {})
            print(f"  Created: {metadata.get('created', 'unknown')}")
            print(f"  Articles: {metadata.get('n_articles', 'unknown')}")
        else:
            print(f"\n⚠ CB Bundle: NOT FOUND")
            print(f"  {msg}")
            print(f"  (CB artifacts not yet available from Kaggle)")

        return all_valid


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Bundle model artifacts into joblib files for faster loading"
    )
    parser.add_argument(
        "--cf-only", action="store_true", help="Only bundle CF models, skip CB"
    )
    parser.add_argument(
        "--no-compress", action="store_true", help="Don't compress bundles"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only verify bundles, don't create new ones",
    )

    args = parser.parse_args()

    # Setup paths
    script_dir = Path(__file__).resolve().parent
    backend_dir = script_dir.parent
    project_root = backend_dir.parent
    cf_dir = project_root / "data" / "recommendations"
    cb_dir = project_root / "data" / "content_based_model"
    output_dir = cf_dir  # Save bundles in same directory as artifacts

    bundler = ModelBundler(cf_dir=str(cf_dir), cb_dir=str(cb_dir), output_dir=str(output_dir))

    if args.verify:
        bundler.verify_bundles()
        return 0

    # Bundle CF
    cf_success = bundler.bundle_cf_models(compress=not args.no_compress)

    if cf_success:
        logger.info("\n✓ CF bundling completed successfully")
    else:
        logger.error("\n✗ CF bundling failed")
        return 1

    # Bundle CB (unless --cf-only specified)
    if args.cf_only:
        logger.info("Skipping CB bundling (--cf-only specified)")
    else:
        cb_success = bundler.bundle_cb_models(compress=not args.no_compress)
        if cb_success:
            logger.info("\n✓ CB bundling completed successfully")
        elif not (cb_dir / "article_similarity_matrix.npy").exists():
            logger.info(
                "\n⚠ CB bundling skipped (artifacts not yet available from Kaggle)"
            )
        else:
            logger.error("\n✗ CB bundling failed")
            return 1

    # Verify
    logger.info("\nVerifying bundles...")
    bundler.verify_bundles()

    print("\n" + "="*70)
    print("✓ BUNDLING COMPLETE")
    print("="*70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
