from fastapi import APIRouter
from app.utils.sentiment_loader import sentiment_models
from app.db.connection import get_db

router = APIRouter(prefix="/sentiment", tags=["Sentiment"])

# ------------------- Predict sentiment -------------------

@router.post("/predict")
def predict_sentiment(payload: dict):
    text = payload.get("text")
    if not text:
        return {"error": "text is required"}

    bert = sentiment_models.predict_bert(text)
    tfidf = sentiment_models.predict_tfidf(text)

    return {
        "bert_prediction": bert,
        "tfidf_predictions": tfidf
    }

# ------------------- Product sentiment summary -------------------

@router.get("/product/{product_id}/summary")
def sentiment_summary(product_id: str, db=next(get_db())):

    sql = f"""
        SELECT sentiment_label 
        FROM niche_data.reviews 
        WHERE article_id = '{product_id}'
    """
    df = db.execute(sql).fetchall()

    if not df:
        return {"message": "No reviews found"}

    labels = [row[0] for row in df]

    total = len(labels)
    pos = labels.count("positive")
    neu = labels.count("neutral")
    neg = labels.count("negative")

    return {
        "product_id": product_id,
        "total_reviews": total,
        "positive": round(pos/total*100, 2),
        "neutral": round(neu/total*100, 2),
        "negative": round(neg/total*100, 2)
    }

# ------------------- Sentiment histogram (chart) -------------------

@router.get("/product/{product_id}/distribution")
def sentiment_distribution(product_id: str, db=next(get_db())):
    sql = f"""
        SELECT sentiment_score 
        FROM niche_data.reviews 
        WHERE article_id = '{product_id}'
    """
    df = db.execute(sql).fetchall()

    scores = [float(row[0]) for row in df]

    return {
        "product_id": product_id,
        "scores": scores  # frontend will convert to histogram
    }

# ------------------- Reviews sorted by sentiment -------------------

@router.get("/product/{product_id}/reviews")
def sentiment_sorted_reviews(product_id: str, order: str = "positive", db=next(get_db())):

    if order == "positive":
        sort = "sentiment_score DESC"
    elif order == "negative":
        sort = "sentiment_score ASC"
    else:
        sort = "created_at DESC"

    sql = f"""
        SELECT review_id, review_text, sentiment_label, sentiment_score 
        FROM niche_data.reviews
        WHERE article_id = '{product_id}'
        ORDER BY {sort}
        LIMIT 200;
    """

    rows = db.execute(sql).fetchall()

    return {"reviews": [dict(r) for r in rows]}
