"""
Model persistence utilities using joblib for hybrid recommendation system.

Handles serialization/deserialization of CF and CB models with compression,
validation, and metadata tracking.
"""

import joblib
import numpy as np
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class ModelPersistence:
    """Utilities for saving and loading ML models with joblib"""

    @staticmethod
    def save_cf_bundle(
        output_path: str,
        recs_df: pd.DataFrame,
        user_factors: np.ndarray,
        item_factors: np.ndarray,
        item_similarity: np.ndarray,
        customer_mapping: Dict[str, int],
        item_mapping: Dict[str, int],
        compress: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str]:
        """
        Save all CF models as a single joblib bundle.

        Args:
            output_path: Path to save the bundle
            recs_df: Recommendations DataFrame
            user_factors: User latent factors (n_users × n_factors)
            item_factors: Item latent factors (n_items × n_factors)
            item_similarity: Item similarity matrix (n_items × n_items)
            customer_mapping: Dict mapping customer_id → index
            item_mapping: Dict mapping article_id → index
            compress: Whether to compress (creates .gz file)
            metadata: Optional metadata dict (version, date, etc)

        Returns:
            Tuple[success: bool, message: str]
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Create metadata
            if metadata is None:
                metadata = {}

            default_metadata = {
                "created": datetime.now().isoformat(),
                "n_users": len(customer_mapping),
                "n_items": len(item_mapping),
                "n_recommendations": len(recs_df),
                "user_factors_shape": user_factors.shape,
                "item_factors_shape": item_factors.shape,
                "item_similarity_shape": item_similarity.shape if item_similarity is not None else None,
                "model_type": "cf_bundle",
                "joblib_version": joblib.__version__,
            }
            default_metadata.update(metadata)

            # Compute content hash for validation (lightweight - just first KB)
            try:
                # Use only a small sample for hashing to save time
                sample_hash = str(user_factors.shape) + str(item_factors.shape)
                content_hash = hashlib.md5(sample_hash.encode()).hexdigest()
            except:
                content_hash = "unknown"
            default_metadata["content_hash"] = content_hash

            # Bundle all models
            bundle = {
                "recs_df": recs_df,
                "user_factors": user_factors,
                "item_factors": item_factors,
                "item_similarity": item_similarity,
                "customer_mapping": customer_mapping,
                "item_mapping": item_mapping,
                "metadata": default_metadata,
            }

            # Determine compression
            compress_level = 3 if compress else 0
            file_ext = ".gz" if compress else ""

            # Save bundle
            joblib.dump(bundle, str(output_path) + file_ext, compress=compress_level)

            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            message = (
                f"✓ CF bundle saved: {output_path}{file_ext} ({file_size_mb:.1f} MB)"
            )
            logger.info(message)
            return True, message

        except Exception as e:
            message = f"✗ Failed to save CF bundle: {str(e)}"
            logger.error(message)
            return False, message

    @staticmethod
    def load_cf_bundle(bundle_path: str) -> Tuple[Optional[Dict], str]:
        """
        Load CF models from joblib bundle.

        Args:
            bundle_path: Path to the bundle file

        Returns:
            Tuple[bundle_dict or None, message: str]
        """
        try:
            bundle_path = Path(bundle_path)

            if not bundle_path.exists():
                # Try with .gz extension
                if not Path(str(bundle_path) + ".gz").exists():
                    message = (
                        f"✗ CF bundle not found: {bundle_path} or {bundle_path}.gz"
                    )
                    logger.warning(message)
                    return None, message
                bundle_path = Path(str(bundle_path) + ".gz")

            # Load bundle
            bundle = joblib.load(str(bundle_path))

            # Validate
            if not isinstance(bundle, dict):
                message = f"✗ Invalid bundle format: {type(bundle)}"
                logger.error(message)
                return None, message

            required_keys = [
                "recs_df",
                "user_factors",
                "item_factors",
                "item_similarity",
                "customer_mapping",
                "item_mapping",
                "metadata",
            ]
            if not all(k in bundle for k in required_keys):
                message = f"✗ Bundle missing required keys. Found: {list(bundle.keys())}"
                logger.error(message)
                return None, message

            metadata = bundle.get("metadata", {})
            file_size_mb = bundle_path.stat().st_size / (1024 * 1024)
            message = (
                f"✓ CF bundle loaded: {bundle_path} ({file_size_mb:.1f} MB) | "
                f"Users: {metadata.get('n_users', 'unknown')}, "
                f"Items: {metadata.get('n_items', 'unknown')}"
            )
            logger.info(message)

            return bundle, message

        except Exception as e:
            message = f"✗ Failed to load CF bundle: {str(e)}"
            logger.error(message)
            return None, message

    @staticmethod
    def save_cb_bundle(
        output_path: str,
        article_similarity: np.ndarray,
        article_embeddings: np.ndarray,
        tfidf_vectorizer: Any,
        price_scaler: Any,
        article_id_to_idx: Dict[str, int],
        config: Optional[Dict[str, Any]] = None,
        compress: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str]:
        """
        Save all CB models as a single joblib bundle.

        Args:
            output_path: Path to save the bundle
            article_similarity: Article similarity matrix
            article_embeddings: Article text embeddings
            tfidf_vectorizer: Fitted TF-IDF vectorizer
            price_scaler: Fitted price scaler
            article_id_to_idx: Dict mapping article_id → index
            config: Optional configuration dict
            compress: Whether to compress
            metadata: Optional metadata dict

        Returns:
            Tuple[success: bool, message: str]
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Create metadata
            if metadata is None:
                metadata = {}

            default_metadata = {
                "created": datetime.now().isoformat(),
                "n_articles": len(article_id_to_idx),
                "article_similarity_shape": article_similarity.shape,
                "article_embeddings_shape": article_embeddings.shape,
                "model_type": "cb_bundle",
                "joblib_version": joblib.__version__,
            }
            default_metadata.update(metadata)

            # Compute content hash
            try:
                sample_hash = str(article_similarity.shape)
                content_hash = hashlib.md5(sample_hash.encode()).hexdigest()
            except:
                content_hash = "unknown"
            default_metadata["content_hash"] = content_hash

            # Bundle all models
            bundle = {
                "article_similarity": article_similarity,
                "article_embeddings": article_embeddings,
                "tfidf_vectorizer": tfidf_vectorizer,
                "price_scaler": price_scaler,
                "article_id_to_idx": article_id_to_idx,
                "config": config or {},
                "metadata": default_metadata,
            }

            # Determine compression
            compress_level = 3 if compress else 0
            file_ext = ".gz" if compress else ""

            # Save bundle
            joblib.dump(bundle, str(output_path) + file_ext, compress=compress_level)

            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            message = (
                f"✓ CB bundle saved: {output_path}{file_ext} ({file_size_mb:.1f} MB)"
            )
            logger.info(message)
            return True, message

        except Exception as e:
            message = f"✗ Failed to save CB bundle: {str(e)}"
            logger.error(message)
            return False, message

    @staticmethod
    def load_cb_bundle(bundle_path: str) -> Tuple[Optional[Dict], str]:
        """
        Load CB models from joblib bundle.

        Args:
            bundle_path: Path to the bundle file

        Returns:
            Tuple[bundle_dict or None, message: str]
        """
        try:
            bundle_path = Path(bundle_path)

            if not bundle_path.exists():
                # Try with .gz extension
                if not Path(str(bundle_path) + ".gz").exists():
                    message = (
                        f"✗ CB bundle not found: {bundle_path} or {bundle_path}.gz"
                    )
                    logger.warning(message)
                    return None, message
                bundle_path = Path(str(bundle_path) + ".gz")

            # Load bundle
            bundle = joblib.load(str(bundle_path))

            # Validate
            if not isinstance(bundle, dict):
                message = f"✗ Invalid bundle format: {type(bundle)}"
                logger.error(message)
                return None, message

            required_keys = [
                "article_similarity",
                "article_embeddings",
                "tfidf_vectorizer",
                "price_scaler",
                "article_id_to_idx",
                "metadata",
            ]
            if not all(k in bundle for k in required_keys):
                message = f"✗ Bundle missing required keys. Found: {list(bundle.keys())}"
                logger.error(message)
                return None, message

            metadata = bundle.get("metadata", {})
            file_size_mb = bundle_path.stat().st_size / (1024 * 1024)
            message = (
                f"✓ CB bundle loaded: {bundle_path} ({file_size_mb:.1f} MB) | "
                f"Articles: {metadata.get('n_articles', 'unknown')}"
            )
            logger.info(message)

            return bundle, message

        except Exception as e:
            message = f"✗ Failed to load CB bundle: {str(e)}"
            logger.error(message)
            return None, message

    @staticmethod
    def get_bundle_info(bundle_path: str) -> Dict[str, Any]:
        """
        Get metadata about a joblib bundle without fully loading it.

        Args:
            bundle_path: Path to the bundle file

        Returns:
            Dict with metadata info
        """
        try:
            bundle_path = Path(bundle_path)

            if not bundle_path.exists():
                if Path(str(bundle_path) + ".gz").exists():
                    bundle_path = Path(str(bundle_path) + ".gz")
                else:
                    return {"error": f"Bundle not found: {bundle_path}"}

            # Load only metadata key (faster, but requires full load with joblib)
            bundle = joblib.load(str(bundle_path))
            metadata = bundle.get("metadata", {})

            file_size_mb = bundle_path.stat().st_size / (1024 * 1024)

            return {
                "path": str(bundle_path),
                "size_mb": file_size_mb,
                "metadata": metadata,
                "exists": True,
            }

        except Exception as e:
            return {"error": str(e)}
