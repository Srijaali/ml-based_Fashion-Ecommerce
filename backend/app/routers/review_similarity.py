from fastapi import APIRouter
from app.utils.review_similarity import review_sim
from app.db.connection import get_db
from sentence_transformers import SentenceTransformer

router = APIRouter(prefix="/reviews", tags=["Similar Reviews"])

# Load model only once
encoder = SentenceTransformer("all-MiniLM-L6-v2")

# ------------------- Similar by review ID -------------------

@router.get("/{review_id}/similar")
def get_similar_reviews(review_id: int, k: int = 10, db=next(get_db())):

    results = review_sim.get_similar_by_id(review_id, k)
    if results is None:
        return {"error": "review_id not found"}

    # Fetch full review text for display
    similar_ids = [r["similar_review_id"] for r in results]

    sql = f"""
        SELECT review_id, review_text, sentiment_label, sentiment_score
        FROM niche_data.reviews
        WHERE review_id IN ({','.join(map(str, similar_ids))})
    """

    data = db.execute(sql).fetchall()
    review_dict = {row[0]: dict(row) for row in data}

    # Combine similarity score + review content
    enriched = []
    for r in results:
        rid = r["similar_review_id"]
        enriched.append({
            "review_id": rid,
            "similarity": r["score"],
            "review_text": review_dict[rid]["review_text"],
            "sentiment": review_dict[rid]["sentiment_label"],
            "sentiment_score": review_dict[rid]["sentiment_score"]
        })

    return enriched

# ------------------- Similar for new input text -------------------

@router.post("/similar-text")
def similar_text(payload: dict, k: int = 10):
    text = payload.get("text")
    if not text:
        return {"error": "text is required"}

    results = review_sim.get_similar_by_text(text, encoder, k)
    return results
