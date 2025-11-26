CREATE OR REPLACE FUNCTION niche_data.get_section_categories(section_name TEXT)
RETURNS TABLE (
    category_name TEXT,
    total_products BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT category_name, COUNT(*)
    FROM (
        SELECT
            CASE 
                WHEN product_type_name = 'Hoodie' THEN 'hoodie'
                WHEN product_type_name = 'Jacket' THEN 'jacket'
                WHEN product_type_name = 'Beanie' THEN 'beanie'
                WHEN product_type_name = 'Trousers'
                     AND section_name IN ('Denim Men','Ladies Denim')
                     THEN 'trouser'
                WHEN product_group_name = 'Accessories' THEN 'accessory'
                ELSE NULL
            END AS category_name
        FROM niche_data.get_section_products(section_name)
    ) x
    WHERE category_name IS NOT NULL
    GROUP BY category_name;
END;
$$ LANGUAGE plpgsql STABLE;
