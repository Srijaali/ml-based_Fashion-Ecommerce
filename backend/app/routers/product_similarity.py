from fastapi import APIRouter
from app.utils.product_similarity import product_sim
from app.db.connection import get_db

router = APIRouter(prefix="/products", tags=["Similar Products"])

# ------------------- Similar Products by ID -------------------

@router.get("/{product_id}/similar")
def get_similar_products(product_id: str, k: int = 10, db=next(get_db())):

    results = product_sim.get_similar_by_id(product_id, k)

    if results is None:
        return {"error": "product_id not found"}

    similar_ids = [r["product_id"] for r in results]

    sql = f"""
        SELECT article_id, prod_name, category_id, price
        FROM niche_data.articles
        WHERE article_id IN ({','.join(f"'{p}'" for p in similar_ids)})
    """

    rows = db.execute(sql).fetchall()
    product_info = {row[0]: dict(row) for row in rows}

    enriched = []
    for r in results:
        pid = r["product_id"]
        enriched.append({
            "product_id": pid,
            "similarity": r["similarity"],
            "product": product_info.get(pid)
        })

    return enriched

