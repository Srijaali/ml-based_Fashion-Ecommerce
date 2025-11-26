import pandas as pd
import numpy as np
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:rayyan123@localhost:5432/fashion_db")

sql_demographics = '''
SELECT
    customer_id,
    age,
    active,
    club_member_status,
    fashion_news_frequency,
    signup_date,
    EXTRACT(DAY FROM (CURRENT_DATE - signup_date)) AS signup_age_days
FROM customers;
'''

sql_rfm = '''
WITH tx AS (
    SELECT
        customer_id,
        COUNT(*)                     AS total_transactions,
        SUM(price)                   AS total_amount_spent,
        MIN(t_dat)                   AS first_purchase_date,
        MAX(t_dat)                   AS last_purchase_date
    FROM niche_data.transactions
    GROUP BY customer_id
),
rec AS (
    SELECT
        customer_id,
        total_transactions,
        total_amount_spent,
        first_purchase_date,
        last_purchase_date,
        (CURRENT_DATE - last_purchase_date) AS recency_days  -- integer
    FROM tx
)
SELECT * FROM rec;
'''

sql_orders = '''
WITH orders_base AS (
    SELECT
        o.customer_id,
        COUNT(*) AS total_orders,
        SUM(oi.quantity) AS total_items_bought,
        SUM(o.total_amount) AS total_revenue_from_orders,
        AVG(o.total_amount) AS avg_order_value
    FROM niche_data.orders o
    LEFT JOIN niche_data.order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id
)
SELECT * FROM orders_base;
'''

sql_events = '''
SELECT
    customer_id,
    COUNT(*) AS total_events,
    SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
    SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) AS clicks,
    SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END) AS carts,
    SUM(CASE WHEN event_type = 'buy' THEN 1 ELSE 0 END) AS buys,
    SUM(CASE WHEN event_type = 'wishlist' THEN 1 ELSE 0 END) AS wishlist_events
FROM niche_data.events
GROUP BY customer_id;
'''

sql_top_category = '''
WITH cat_pref AS (
    SELECT
        t.customer_id,
        a.category_id,
        COUNT(*) AS cnt
    FROM niche_data.transactions t
    JOIN niche_data.articles a ON t.article_id = a.article_id
    GROUP BY t.customer_id, a.category_id
),

ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY cnt DESC) AS rnk
    FROM cat_pref
)

SELECT
    customer_id,
    category_id AS top_category
FROM ranked
WHERE rnk = 1;
'''

demographics = pd.read_sql(sql_demographics, engine)
rfm = pd.read_sql(sql_rfm, engine)
orders = pd.read_sql(sql_orders, engine)
events = pd.read_sql(sql_events, engine)
top_cat = pd.read_sql(sql_top_category, engine)


df = (
    demographics
    .merge(rfm, on="customer_id", how="left")
    .merge(orders, on="customer_id", how="left")
    .merge(events, on="customer_id", how="left")
    .merge(top_cat, on="customer_id", how="left")
)


df['R_score'] = pd.qcut(df['recency_days'], q=5, labels=False, duplicates='drop')
df['F_score'] = pd.qcut(df['total_transactions'], q=5, labels=False, duplicates='drop')
df['M_score'] = pd.qcut(df['total_amount_spent'], q=5, labels=False, duplicates='drop')

df['RFM_score'] = df['R_score'] + df['F_score'] + df['M_score']


df.to_parquet("data/ml/customer_features.parquet", index=False)
#df.to_csv("data/ml/customer_features.csv", index=False)
