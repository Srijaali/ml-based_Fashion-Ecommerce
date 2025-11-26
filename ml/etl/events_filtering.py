import pandas as pd
from sqlalchemy import create_engine
import numpy as np


engine = create_engine("postgresql://postgres:rayyan123@localhost:5432/fashion_db")

# events_raw dataset

sql_events = """
SELECT 
    e.event_id,
    e.session_id,
    e.customer_id,
    e.article_id,
    a.category_id,
    e.event_type,
    e.campaign_id,
    e.created_at,
    EXTRACT(HOUR FROM e.created_at) AS event_hour,
    EXTRACT(DOW FROM e.created_at) AS event_day
FROM niche_data.events e
LEFT JOIN niche_data.articles a ON e.article_id = a.article_id
ORDER BY e.customer_id, e.session_id, e.created_at;
"""

events = pd.read_sql(sql_events, engine)

# addinng time since session start
events['created_at'] = pd.to_datetime(events['created_at'])

events['session_start'] = (
    events.groupby('session_id')['created_at'].transform('min')
)

events['time_since_session_start'] = (
    events['created_at'] - events['session_start']
).dt.total_seconds()


# conversion flag
events['is_conversion'] = (events['event_type'] == 'buy').astype(int)

events.to_parquet("data/ml/events/events_raw.parquet", index=False)
#events.to_csv("data/ml/events/events_raw.csv", index=False)




# Session Funnel Dataset
session_funnel = events.groupby(['session_id', 'customer_id']).agg(
    views=('event_type', lambda x: (x=='view').sum()),
    clicks=('event_type', lambda x: (x=='click').sum()),
    carts=('event_type', lambda x: (x=='cart').sum()),
    buys=('event_type', lambda x: (x=='buy').sum()),
    wishlist=('event_type', lambda x: (x=='wishlist').sum()),
    first_event=('created_at', 'min'),
    last_event=('created_at', 'max')
).reset_index()

# Derived Metrics

# Conversion Flag
session_funnel['converted'] = (session_funnel['buys'] > 0).astype(int)

# time to convert=(IF CONVERSION HAPPENS)
session_funnel['time_to_convert'] = np.where(
    session_funnel['converted'] == 1,
    (session_funnel['last_event'] - session_funnel['first_event']).dt.total_seconds(),
    None
)

# Funnel Stage Classification
def stage(row):
    if row['buys'] > 0: return "purchase"
    if row['carts'] > 0: return "cart"
    if row['clicks'] > 0: return "click"
    if row['views'] > 0: return "view"
    return "unknown"

session_funnel['funnel_stage'] = session_funnel.apply(stage, axis=1)

session_funnel.to_parquet("data/ml/events/session_funnel.parquet", index=False)
# session_funnel.to_csv("data/ml/events/session_funnel.csv", index=False)





# Customer Behavioral/Intent Features
customer_events = events.groupby('customer_id').agg(
    total_events=('event_id', 'count'),
    views=('event_type', lambda x: (x=='view').sum()),
    clicks=('event_type', lambda x: (x=='click').sum()),
    carts=('event_type', lambda x: (x=='cart').sum()),
    buys=('event_type', lambda x: (x=='buy').sum()),
    wishlist_events=('event_type', lambda x: (x=='wishlist').sum()),
).reset_index()


# session level features
sessions = session_funnel.groupby('customer_id').agg(
    total_sessions=('session_id', 'count'),
    avg_session_length_seconds=('first_event', lambda x: (session_funnel['last_event'] - session_funnel['first_event']).dt.total_seconds().mean())
).reset_index()

# merge
customer_features = customer_events.merge(sessions, on='customer_id', how='left')


# add conversion metrics
customer_features['conversion_rate'] = customer_features['buys'] / customer_features['views'].replace(0, 1)
customer_features['click_through_rate'] = customer_features['clicks'] / customer_features['views'].replace(0, 1)
customer_features['add_to_cart_rate'] = customer_features['carts'] / customer_features['clicks'].replace(0, 1)
customer_features['cart_abandon_rate'] = 1 - (customer_features['buys'] / customer_features['carts'].replace(0, 1))
customer_features['view_to_buy_rate'] = customer_features['buys'] / customer_features['views'].replace(0, 1)


# dominnant activity per customer
def dom(row):
    actions = ['views', 'clicks', 'carts', 'buys', 'wishlist_events']
    return actions[np.argmax([row[a] for a in actions])]

customer_features['dominant_event_type'] = customer_features.apply(dom, axis=1)


customer_features.to_parquet("data/ml/events/customer_behavior.parquet", index=False)
# customer_features.to_csv("data/ml/events/customer_behavior.csv", index=False)
