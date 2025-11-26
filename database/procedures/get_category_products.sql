CREATE OR REPLACE FUNCTION niche_data.get_category_products(
    section_name TEXT,
    category_name TEXT,
    sort_option TEXT
)
RETURNS TABLE (
    article_id TEXT,
    prod_name TEXT,
    price NUMERIC,
    stock INT,
    average_rating NUMERIC,
    total_reviews INT,
    popularity_score BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH base AS (
        SELECT *
        FROM niche_data.get_section_products(section_name)
        WHERE category = category_name
    )
    SELECT *
    FROM base
    ORDER BY
        CASE WHEN sort_option = 'price_low_high' THEN price END ASC,
        CASE WHEN sort_option = 'price_high_low' THEN price END DESC,
        CASE WHEN sort_option = 'popular' THEN popularity_score END DESC,
        CASE WHEN sort_option = 'newest' THEN article_id END DESC,
        CASE WHEN sort_option = 'best_rated' THEN average_rating END DESC;
END;
$$ LANGUAGE plpgsql STABLE;
