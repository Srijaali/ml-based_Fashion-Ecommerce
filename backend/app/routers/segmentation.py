import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.segmentation import CustomerSegment
from sqlalchemy import func
import pandas as pd
from typing import Dict, Any

router = APIRouter()

# Project-root aware path to segmentation artifacts
HERE = os.path.abspath(os.path.dirname(__file__))            # backend/app/routers
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "../../.."))  # repo root
SEGMENTATION_DIR = os.path.join(PROJECT_ROOT, "data", "ml", "segmentation")
PROFILES_CSV = os.path.join(SEGMENTATION_DIR, "segment_profiles.csv")


# --- Utility: load segment profiles (if available) ---
def load_segment_profiles() -> pd.DataFrame | None:
    try:
        if os.path.exists(PROFILES_CSV):
            df = pd.read_csv(PROFILES_CSV)
            # ensure there's a segment column; if not, try to rename first col
            if "segment" not in df.columns and df.shape[1] > 0:
                df = df.rename(columns={df.columns[0]: "segment"})
            return df
    except Exception:
        pass
    return None


# --- Utility: generate sensible segment labels from profiles ---
def generate_labels_from_profiles(df: pd.DataFrame) -> Dict[int, Dict[str, str]]:
    """
    Create human-friendly names for segments based on monetary/frequency.
    Returns {segment_id: {"name": "...", "description": "..."}}
    """
    labels: Dict[int, Dict[str, str]] = {}
    # choose metric for ordering: monetary then frequency
    sort_key = "monetary" if "monetary" in df.columns else df.columns[1]
    desc = df.sort_values(by=sort_key, ascending=False)

    # heuristics: top -> High-Value, mid -> Steady, bottom -> Dormant
    segments = desc["segment"].tolist()

    mapping_names = {}
    if len(segments) == 1:
        mapping_names[segments[0]] = ("All Customers", "Single cluster covering all customers.")
    elif len(segments) == 2:
        mapping_names[segments[0]] = ("High-Value Loyalists", "Top spenders with frequent purchases.")
        mapping_names[segments[1]] = ("Low-Value / Dormant", "Lower spenders or less engaged customers.")
    else:
        # three or more
        # highest -> VIP, middle(s) -> Steady/Occasional, lowest -> Dormant
        mapping_names[segments[0]] = ("High-Value Loyalists", "High frequency and high spend customers.")
        mapping_names[segments[-1]] = ("Dormant Customers", "Low frequency, low spend; reactivation candidates.")
        # middle segments get Steady / Occasional naming
        for s in segments[1:-1]:
            mapping_names[s] = ("Steady Buyers", "Moderate spenders with regular activity.")

    # build descriptions, optionally extend by showing 1-2 stat highlights
    for seg_id, (name, short_desc) in mapping_names.items():
        # try to pick a few stats to mention
        row = df[df["segment"] == seg_id]
        if not row.empty:
            try:
                rec = int(round(float(row.iloc[0].get("recency_days", 0))))
                freq = float(row.iloc[0].get("frequency", 0))
                mon = float(row.iloc[0].get("monetary", 0))
                extra = f" Avg recency: {rec} days · Avg freq: {freq:.1f} · Avg monetary: {mon:.2f}"
                description = short_desc + extra
            except Exception:
                description = short_desc
        else:
            description = short_desc
        labels[int(seg_id)] = {"name": name, "description": description}

    return labels


# --- Fallback static labels (if no profiles CSV) ---
FALLBACK_LABELS = {
    0: {"name": "Steady Buyers", "description": "Regular customers with moderate activity."},
    1: {"name": "High-Value Loyalists", "description": "Frequent buyers with high spend (VIP)."},
    2: {"name": "Dormant Customers", "description": "Low engagement customers; reactivation targets."},
}


# Precompute labels on import (attempt from CSV first)
_profiles_df = load_segment_profiles()
if _profiles_df is not None:
    try:
        SEGMENT_LABELS = generate_labels_from_profiles(_profiles_df)
    except Exception:
        SEGMENT_LABELS = FALLBACK_LABELS
else:
    SEGMENT_LABELS = FALLBACK_LABELS


# ---------------------------
# Endpoints
# ---------------------------

@router.get("/customer/{customer_id}")
def get_customer_segment(customer_id: str, db: Session = Depends(get_db)):
    seg = (
        db.query(CustomerSegment)
        .filter(CustomerSegment.customer_id == customer_id)
        .first()
    )

    if not seg:
        raise HTTPException(status_code=404, detail="Customer not found")

    label = SEGMENT_LABELS.get(int(seg.segment), {"name": "Unknown", "description": ""})
    return {
        "customer_id": seg.customer_id,
        "segment_id": seg.segment,
        "segment_label": label["name"],
        "segment_description": label["description"],
        "updated_at": seg.updated_at,
    }


@router.get("/segments/overview")
def get_segment_overview(db: Session = Depends(get_db)):
    overview = (
        db.query(CustomerSegment.segment, func.count(CustomerSegment.segment).label("count"))
        .group_by(CustomerSegment.segment)
        .order_by(CustomerSegment.segment)
        .all()
    )

    # return with labels
    return {
        "segments": [
            {
                "segment_id": int(seg),
                "segment_label": SEGMENT_LABELS.get(int(seg), {"name": "Unknown"})["name"],
                "count": int(cnt)
            }
            for seg, cnt in overview
        ]
    }


@router.get("/definitions")
def get_segment_definitions():
    """
    Returns the mapping segment_id -> {name, description}
    Frontend should call this once (cached for 24h) to display labels.
    """
    # ensure labels reflect latest CSV if someone updated the file while server running
    df = load_segment_profiles()
    if df is not None:
        try:
            labels = generate_labels_from_profiles(df)
        except Exception:
            labels = SEGMENT_LABELS
    else:
        labels = SEGMENT_LABELS

    # convert keys to strings for JSON stability
    return {str(k): v for k, v in labels.items()}


@router.get("/profiles")
def get_segment_profiles():
    """
    Returns the full segment_profiles.csv as JSON list (one row per segment).
    Useful for admin dashboard visualization.
    """
    if not os.path.exists(PROFILES_CSV):
        raise HTTPException(status_code=404, detail="segment_profiles.csv not found on server")

    try:
        df = pd.read_csv(PROFILES_CSV)
        # Convert dataframe to records (cast numpy types to python native)
        records = df.fillna("").to_dict(orient="records")
        # ensure segment is int
        for r in records:
            if "segment" in r:
                r["segment"] = int(r["segment"])
        return {"profiles": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read profiles: {e}")
