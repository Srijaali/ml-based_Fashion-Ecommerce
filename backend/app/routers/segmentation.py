from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.segmentation import CustomerSegment
from typing import List, Optional

router = APIRouter()

SEGMENT_LABELS = {
    0: "Steady Buyers",
    1: "High-Value Loyalists",
    2: "Dormant Customers",
}

@router.get("/segments/customer/{customer_id}")
def get_customer_segment(customer_id: str, db: Session = Depends(get_db)):
    seg = (
        db.query(CustomerSegment)
        .filter(CustomerSegment.customer_id == customer_id)
        .first()
    )

    if not seg:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "customer_id": seg.customer_id,
        "segment_id": seg.segment,
        "segment_label": SEGMENT_LABELS.get(seg.segment, "Unknown Segment"),
        "updated_at": seg.updated_at,
    }


@router.get("/segments/overview")
def get_segment_overview(db: Session = Depends(get_db)):
    from sqlalchemy import func

    overview = (
        db.query(
            CustomerSegment.segment,
            func.count().label("count")
        )
        .group_by(CustomerSegment.segment)
        .order_by(CustomerSegment.segment)
        .all()
    )

    return {
        "segments": [
            {
                "segment_id": seg,
                "segment_label": SEGMENT_LABELS.get(seg, "Unknown"),
                "count": cnt
            }
            for seg, cnt in overview
        ]
    }

