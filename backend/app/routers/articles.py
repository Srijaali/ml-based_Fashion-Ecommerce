from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models.articles import Article
from app.schemas.articles_schema import ArticleCreate, ArticleUpdate, ArticleResponse,    ArticlePerformanceResponse,ArticleDemandTrendResponse,ArticleInventoryResponse,ArticleFunnelMetricsResponse
from app.actions import products as product_actions
from app.dependencies import get_current_admin, AdminResponse


router = APIRouter()


# --------------------------------------------------------
# GET all articles
# --------------------------------------------------------
@router.get("/", response_model=List[ArticleResponse])
def get_articles(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return (
        db.query(Article)
        .order_by(Article.article_id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# --------------------------------------------------------
# GET articles by product name (returns LIST)
# --------------------------------------------------------
@router.get("/by-name/{prod_name}", response_model=List[ArticleResponse])
def get_articles_by_name(prod_name: str, db: Session = Depends(get_db)):
    articles = db.query(Article).filter(Article.prod_name == prod_name).all()

    if not articles:
        raise HTTPException(status_code=404, detail="No articles found")

    return articles


# --------------------------------------------------------
# GET single article by article_id
# --------------------------------------------------------
@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: str, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.article_id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return article



# --------------------------------------------------------
# CREATE article (Admin only)
# --------------------------------------------------------
@router.post("/", response_model=ArticleResponse)
def create_article(
    payload: ArticleCreate, 
    current_admin: AdminResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    article = Article(**payload.dict())
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


# --------------------------------------------------------
# UPDATE article (Admin only)
# --------------------------------------------------------
@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: str, 
    payload: ArticleUpdate, 
    current_admin: AdminResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    article = db.query(Article).filter(Article.article_id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(article, key, value)

    db.commit()
    db.refresh(article)
    return article


# --------------------------------------------------------
# DELETE article (Admin only)
# --------------------------------------------------------
@router.delete("/{article_id}")
def delete_article(
    article_id: str, 
    current_admin: AdminResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    article = db.query(Article).filter(Article.article_id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(article)
    db.commit()
    return {"message": "Article deleted successfully"}



# -----------------------------------------------------------------
# PERFORMANCE VIEW
# -----------------------------------------------------------------
@router.get("/{article_id}/performance", response_model=ArticlePerformanceResponse)
def get_performance(article_id: str, db: Session = Depends(get_db)):
    data = product_actions.get_article_performance(article_id, db)
    if not data:
        raise HTTPException(404, "Performance data not found")
    return data
#performance working

# -----------------------------------------------------------------
# DEMAND TREND VIEW
# -----------------------------------------------------------------
@router.get("/{article_id}/demand-trend", response_model=List[ArticleDemandTrendResponse])
def get_demand(article_id: str, db: Session = Depends(get_db)):
    return product_actions.get_demand_trend(article_id, db)

#demand is empty 

# -----------------------------------------------------------------
# INVENTORY STATUS VIEW
# -----------------------------------------------------------------
@router.get("/{article_id}/inventory", response_model=ArticleInventoryResponse)
def get_inventory(article_id: str, db: Session = Depends(get_db)):
    data = product_actions.get_inventory_status(article_id, db)
    if not data:
        raise HTTPException(404, "Inventory data not found")
    return data
#working correct

# -----------------------------------------------------------------
# FUNNEL METRICS VIEW
# -----------------------------------------------------------------
@router.get("/funnel-metrics", response_model=ArticleFunnelMetricsResponse)
def get_funnel_metrics(db: Session = Depends(get_db)):
    data = product_actions.get_funnel_metrics(db)

    if not data:
        raise HTTPException(status_code=404, detail="Funnel metrics not found")

    return data #not working 404 not found

