CREATE OR REPLACE FUNCTION niche_data.get_sections()
RETURNS TABLE (
    section_id INT,
    section_name TEXT,
    display_name TEXT,
    total_products BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM (
        SELECT 
            1 AS section_id,
            'men' AS section_name,
            'Men' AS display_name,
            COUNT(*) AS total_products
        FROM niche_data.articles
        WHERE section_name ILIKE '%Men%'
           OR section_name ILIKE '%Boy%'
           OR section_name IN ('Men Underwear','Men Shoes','Mens Outerwear','Men H&M Sport')

        UNION ALL
        SELECT
            2, 'women', 'Women',
            COUNT(*) FROM niche_data.articles
        WHERE section_name ILIKE '%Women%'
           OR section_name ILIKE '%Ladies%'
           OR section_name ILIKE 'H&M+%'
           OR section_name = 'Mama'

        UNION ALL
        SELECT
            3, 'kids', 'Kids',
            COUNT(*) FROM niche_data.articles
        WHERE section_name ILIKE '%Kids%'
           OR section_name ILIKE '%Baby%'
           OR section_name IN ('Young Girl','Young Boy','Kids Boy','Kids Girl')

        UNION ALL
        SELECT
            4, 'unisex', 'Unisex',
            COUNT(*) FROM niche_data.articles
        WHERE article_id NOT IN (
            SELECT article_id FROM niche_data.articles WHERE
                product_group_name = 'Accessories'
                OR section_name ILIKE '%Men%'
                OR section_name ILIKE '%Women%'
                OR section_name ILIKE '%Kids%'
                OR section_name ILIKE '%Boy%'
                OR section_name ILIKE '%Girl%'
                OR section_name ILIKE '%Baby%'
        )

        UNION ALL
        SELECT
            5, 'accessories', 'Accessories',
            COUNT(*) FROM niche_data.articles
        WHERE product_group_name = 'Accessories'
    ) AS s;
END;
$$ LANGUAGE plpgsql STABLE;
