CREATE OR REPLACE FUNCTION niche_data.get_section_products(section_name TEXT)
RETURNS TABLE (
    article_id TEXT,
    prod_name TEXT,
    price NUMERIC,
    category TEXT,
    final_section TEXT,
    stock INT,
    average_rating NUMERIC,
    total_reviews INT,
    popularity_score BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.article_id,
        a.prod_name,
        a.price,
        CASE 
            WHEN a.product_type_name = 'Hoodie' THEN 'hoodie'
            WHEN a.product_type_name = 'Jacket' THEN 'jacket'
            WHEN a.product_type_name = 'Beanie' THEN 'beanie'
            WHEN a.product_type_name = 'Trousers'
                 AND a.section_name IN ('Denim Men','Ladies Denim')
                 THEN 'trouser'
            WHEN a.product_group_name = 'Accessories' THEN 'accessory'
            ELSE 'other'
        END AS category,
        section_name,
        a.stock,

        -- Avg Rating
        (SELECT AVG(r.rating)::NUMERIC 
         FROM niche_data.reviews r 
         WHERE r.article_id = a.article_id) AS average_rating,

        -- Total Reviews
        (SELECT COUNT(*) FROM niche_data.reviews r 
         WHERE r.article_id = a.article_id) AS total_reviews,

        -- Popularity
        (SELECT COUNT(*) FROM niche_data.transactions t
         WHERE t.article_id = a.article_id) AS popularity_score

    FROM niche_data.articles a
    WHERE 
        (section_name = 'men' AND (
            a.section_name ILIKE '%Men%'
            OR a.section_name ILIKE '%Boy%'
            OR a.section_name IN ('Men Underwear','Men Shoes','Mens Outerwear','Men H&M Sport')
        ))
        OR (section_name = 'women' AND (
            a.section_name ILIKE '%Women%'
            OR a.section_name ILIKE '%Ladies%'
            OR a.section_name ILIKE 'H&M+%'
            OR a.section_name = 'Mama'
        ))
        OR (section_name = 'kids' AND (
            a.section_name ILIKE '%Kids%'
            OR a.section_name ILIKE '%Baby%'
            OR a.section_name IN ('Young Girl','Young Boy','Kids Boy','Kids Girl')
        ))
        OR (section_name = 'accessories' AND a.product_group_name = 'Accessories')
        OR (section_name = 'unisex' AND a.product_group_name <> 'Accessories');
END;
$$ LANGUAGE plpgsql STABLE;
