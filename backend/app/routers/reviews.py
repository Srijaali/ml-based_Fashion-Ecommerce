from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text
from app.db.database import get_db
from app.db.models.reviews import Review
from app.schemas.reviews_schema import ReviewCreate, ReviewOut,ReviewBase,ReviewUpdate

router = APIRouter()

@router.get("/", response_model=List[ReviewOut])
def get_all_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Review).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()


# ---------------------------
# GET REVIEWS FOR ARTICLE
# ---------------------------
@router.get("/article/{article_id}", response_model=List[ReviewOut])
def get_reviews_by_article(article_id: str, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.article_id == article_id).order_by(Review.created_at.desc()).all()


# ---------------------------
# GET REVIEWS FOR CUSTOMER
# ---------------------------
@router.get("/customer/{customer_id}", response_model=List[ReviewOut])
def get_reviews_by_customer(customer_id: str, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.customer_id == customer_id).order_by(Review.created_at.desc()).all()

# get review by review id
@router.get("/{review_id}", response_model=ReviewOut)
def get_review(review_id: str, db: Session = Depends(get_db)):
    db_review = db.query(Review).filter(Review.review_id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="review not found")
    return db_review


# ---------------------------
# CREATE REVIEW (with auto-rating)
# ---------------------------
@router.post("/", response_model=ReviewOut, status_code=201)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)):

    # call DB function to generate rating and insert review
    sql = text("""
        SELECT niche_data.add_review(
            :cid,
            :aid,
            :txt
        )
    """)

    db.execute(sql, {
        "cid": payload.customer_id,
        "aid": payload.article_id,
        "txt": payload.review_text
    })
    db.commit()

    # fetch the created review
    row = db.execute(text("""
        SELECT *
        FROM niche_data.reviews
        WHERE customer_id = :cid AND article_id = :aid
        ORDER BY created_at DESC
        LIMIT 1
    """), {
        "cid": payload.customer_id,
        "aid": payload.article_id
    }).mappings().first()

    if not row:
        raise HTTPException(500, "Review not inserted")

    return row

# ---------------------------
# UPDATE REVIEW
# ---------------------------
@router.put("/{review_id}", response_model=ReviewOut)
def update_review(review_id: int, payload: ReviewUpdate, db: Session = Depends(get_db)):

    # if text updated → regenerate rating
    if payload.review_text:
        sql = text("""
            UPDATE niche_data.reviews
            SET review_text = :txt,
                rating = niche_data.generate_rating_from_text(:txt)
            WHERE review_id = :rid
            RETURNING *
        """)
        row = db.execute(sql, {
            "rid": review_id,
            "txt": payload.review_text
        }).mappings().first()
    else:
        sql = text("""
            UPDATE niche_data.reviews
            SET rating = :rating
            WHERE review_id = :rid
            RETURNING *
        """)
        row = db.execute(sql, {
            "rid": review_id,
            "rating": payload.rating
        }).mappings().first()

    db.commit()

    if not row:
        raise HTTPException(404, "Review not found")

    return row


# ---------------------------
# DELETE REVIEW
# ---------------------------
@router.delete("/{review_id}", status_code=200)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("""
        DELETE FROM niche_data.reviews
        WHERE review_id = :rid
    """), {"rid": review_id})

    db.commit()

    if result.rowcount == 0:
        raise HTTPException(404, "Review not found")

    return {"detail": f"Review {review_id} deleted successfully"}

#---------------------------
# ANALYTICS → AVG RATING OF AN ARTICLE
# ---------------------------
@router.get("/analytics/article/{article_id}")
def get_article_rating_stats(article_id: str, db: Session = Depends(get_db)):
    sql = text("""
        SELECT 
            AVG(rating) AS avg_rating,
            COUNT(*) AS total_reviews
        FROM niche_data.reviews
        WHERE article_id = :aid
    """)
    row = db.execute(sql, {"aid": article_id}).mappings().first()

    return {
        "article_id": article_id,
        "avg_rating": round(float(row["avg_rating"]), 2) if row["avg_rating"] else None,
        "total_reviews": row["total_reviews"]
    }

'''
@router.post("/", response_model=ReviewOut)
def add_review(review: ReviewCreate, db: Session = Depends(get_db)):
    db_review = Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@router.put("/{review_id}", response_model=ReviewOut)
def update_review(review_id: int, review: ReviewCreate, db: Session = Depends(get_db)):
    db_review = db.query(Review).filter(Review.review_id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    for key, value in review.dict().items():
        setattr(db_review, key, value)
    db.commit()
    db.refresh(db_review)
    return db_review

@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    db_review = db.query(Review).filter(Review.review_id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(db_review)
    db.commit()
    return {"detail": "Review deleted successfully"}
'''