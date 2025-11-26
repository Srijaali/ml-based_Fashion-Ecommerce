from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.sections_schema import (
    ALLOWED_CATEGORIES,
    ALLOWED_SECTIONS,
    ALLOWED_SORT_OPTIONS,
    CategoryProduct,
    CategoryProductsResponse,
    FilterOptions,
    FilterOptionsResponse,
    FilterRange,
    FilterSortProduct,
    FilterSortRequest,
    FilterSortResponse,
    PopularityRange,
    SectionCategoriesResponse,
    SectionCategorySummary,
    SectionProduct,
    SectionProductsResponse,
    SectionItem,
    SectionsResponse,
)
from app.utils.cache import cache_get, cache_set


router = APIRouter(prefix="/sections", tags=["Sections & Catalog"])


def _validate_section(section_name: str) -> str:
    if section_name not in ALLOWED_SECTIONS:
        raise HTTPException(status_code=404, detail="Section not found")
    return section_name


def _validate_category(category_name: str) -> str:
    if category_name not in ALLOWED_CATEGORIES:
        # Category exists but is not supported by UX → treat as bad input
        raise HTTPException(status_code=400, detail="Invalid category")
    return category_name


def _normalize_sort_option(sort_option: str | None) -> str:
    if not sort_option:
        return "popular"
    if sort_option not in ALLOWED_SORT_OPTIONS:
        # Fallback to default sorting as per spec
        return "popular"
    return sort_option


@router.get("/", response_model=SectionsResponse)
def get_sections(db: Session = Depends(get_db)) -> SectionsResponse:
    """
    Return the list of high-level sections with product counts.
    Backed by niche_data.get_sections().
    """
    cache_key = "sections:v1"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    sql = text("SELECT * FROM niche_data.get_sections()")
    rows = db.execute(sql).mappings().all()

    sections: List[SectionItem] = [
        SectionItem(
            id=row["section_id"],
            name=row["section_name"],
            display=row["display_name"],
            total_products=int(row["total_products"]),
        )
        for row in rows
    ]

    response = SectionsResponse(sections=sections)
    # Cache for 24 hours
    cache_set(cache_key, response, ttl_seconds=24 * 60 * 60)
    return response


@router.get("/{section_name}/products", response_model=SectionProductsResponse)
def get_section_products(
    section_name: str,
    db: Session = Depends(get_db),
    limit: int = Query(24, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> SectionProductsResponse:
    """
    Product listing for a section.
    Backed by niche_data.get_section_products(section_name).
    """
    section = _validate_section(section_name)

    cache_key = f"section_products:v1:{section}:{limit}:{offset}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    sql = text("SELECT * FROM niche_data.get_section_products(:section_name)")
    rows = db.execute(sql, {"section_name": section}).mappings().all()

    total_products = len(rows)
    window = rows[offset : offset + limit]

    products: List[SectionProduct] = [
        SectionProduct(
            article_id=row["article_id"],
            prod_name=row["prod_name"],
            price=float(row["price"]),
            category=row["category"],
            section_name=row["final_section"],
            stock=row["stock"],
            average_rating=float(row["average_rating"]) if row["average_rating"] is not None else None,
            total_reviews=row["total_reviews"],
            popularity_score=row["popularity_score"],
        )
        for row in window
    ]

    response = SectionProductsResponse(
        section=section,
        total_products=total_products,
        products=products,
    )
    # Cache for 30 seconds
    cache_set(cache_key, response, ttl_seconds=30)
    return response


@router.get("/{section_name}/categories", response_model=SectionCategoriesResponse)
def get_section_categories(
    section_name: str,
    db: Session = Depends(get_db),
) -> SectionCategoriesResponse:
    """
    Category summary for a section with product counts.
    Backed by niche_data.get_section_categories(section_name).
    """
    section = _validate_section(section_name)

    cache_key = f"section_categories:v1:{section}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    sql = text("SELECT * FROM niche_data.get_section_categories(:section_name)")
    rows = db.execute(sql, {"section_name": section}).mappings().all()

    categories: List[SectionCategorySummary] = [
        SectionCategorySummary(
            category=row["category_name"],
            total_products=int(row["total_products"]),
        )
        for row in rows
    ]

    response = SectionCategoriesResponse(section=section, categories=categories)
    # Cache for 1 hour
    cache_set(cache_key, response, ttl_seconds=60 * 60)
    return response


@router.get("/{section_name}/{category_name}/products", response_model=CategoryProductsResponse)
def get_category_products(
    section_name: str,
    category_name: str,
    sort: str | None = Query("popular"),
    db: Session = Depends(get_db),
    limit: int = Query(24, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> CategoryProductsResponse:
    """
    Product listing for a section + category combination.
    Backed by niche_data.get_category_products(section, category, sort_option).
    """
    section = _validate_section(section_name)
    category = _validate_category(category_name)
    sort_option = _normalize_sort_option(sort)

    cache_key = f"category_products:v1:{section}:{category}:{sort_option}:{limit}:{offset}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    sql = text(
        """
        SELECT * 
        FROM niche_data.get_category_products(:section_name, :category_name, :sort_option)
        """
    )
    rows = db.execute(
        sql,
        {"section_name": section, "category_name": category, "sort_option": sort_option},
    ).mappings().all()

    total = len(rows)
    window = rows[offset : offset + limit]

    products: List[CategoryProduct] = [
        CategoryProduct(
            article_id=row["article_id"],
            prod_name=row["prod_name"],
            price=float(row["price"]),
            stock=row["stock"],
            average_rating=float(row["average_rating"]) if row["average_rating"] is not None else None,
            total_reviews=row["total_reviews"],
            popularity_score=row["popularity_score"],
        )
        for row in window
    ]

    response = CategoryProductsResponse(
        section=section,
        category=category,
        sorting=sort_option,
        products=products,
    )
    # Cache for ~20 seconds (within 15–30s guidance)
    cache_set(cache_key, response, ttl_seconds=20)
    return response


@router.get("/{section_name}/{category_name}/filters", response_model=FilterOptionsResponse)
def get_filter_options(
    section_name: str,
    category_name: str,
    db: Session = Depends(get_db),
) -> FilterOptionsResponse:
    """
    Return min/max ranges for price, rating and popularity for a section/category.
    Backed by niche_data.get_filter_options(section, category).
    """
    section = _validate_section(section_name)
    category = _validate_category(category_name)

    cache_key = f"filter_options:v1:{section}:{category}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    sql = text(
        """
        SELECT * 
        FROM niche_data.get_filter_options(:section_name, :category_name)
        """
    )
    row = db.execute(
        sql, {"section_name": section, "category_name": category}
    ).mappings().first()

    # Handle no data: return empty ranges but keep 200 for a valid (section, category)
    if not row:
        filters = FilterOptions(
            price=FilterRange(min=None, max=None),
            rating=FilterRange(min=None, max=None),
            popularity=PopularityRange(min=None, max=None),
        )
    else:
        filters = FilterOptions(
            price=FilterRange(
                min=float(row["min_price"]) if row["min_price"] is not None else None,
                max=float(row["max_price"]) if row["max_price"] is not None else None,
            ),
            rating=FilterRange(
                min=float(row["min_rating"]) if row["min_rating"] is not None else None,
                max=float(row["max_rating"]) if row["max_rating"] is not None else None,
            ),
            popularity=PopularityRange(
                min=int(row["min_popularity"]) if row["min_popularity"] is not None else None,
                max=int(row["max_popularity"]) if row["max_popularity"] is not None else None,
            ),
        )

    response = FilterOptionsResponse(category=category, filters=filters)
    # Cache for 5 minutes
    cache_set(cache_key, response, ttl_seconds=5 * 60)
    return response


@router.post("/{section_name}/{category_name}/filter-sort", response_model=FilterSortResponse)
def filter_and_sort_products(
    section_name: str,
    category_name: str,
    payload: FilterSortRequest,
    db: Session = Depends(get_db),
) -> FilterSortResponse:
    """
    Filter and sort products for a section/category by price range and sort option.
    Backed by niche_data.filter_and_sort_products(...).
    """
    section = _validate_section(section_name)
    category = _validate_category(category_name)

    if payload.price_max < payload.price_min:
        raise HTTPException(status_code=400, detail="price_max must be >= price_min")

    sort_option = _normalize_sort_option(payload.sort_option)

    sql = text(
        """
        SELECT *
        FROM niche_data.filter_and_sort_products(
            :section_name,
            :category_name,
            :price_min,
            :price_max,
            :sort_option
        )
        """
    )
    rows = db.execute(
        sql,
        {
            "section_name": section,
            "category_name": category,
            "price_min": payload.price_min,
            "price_max": payload.price_max,
            "sort_option": sort_option,
        },
    ).mappings().all()

    products: List[FilterSortProduct] = [
        FilterSortProduct(
            article_id=row["article_id"],
            prod_name=row["prod_name"],
            price=float(row["price"]),
            stock=row["stock"],
            average_rating=float(row["average_rating"]) if row["average_rating"] is not None else None,
            total_reviews=row["total_reviews"],
            popularity_score=row["popularity_score"],
        )
        for row in rows
    ]

    return FilterSortResponse(products=products)


