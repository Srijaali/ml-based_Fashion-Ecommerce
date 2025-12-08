import pandas as pd

df = pd.read_csv('data/recommendations/recommendations.csv')
print(f'Total recommendations: {len(df)}')
print(f'\nColumns: {df.columns.tolist()}')
print(f'\nDataframe info:')
print(df.head(10))
print(f'\nSample customer: {df["customer_id"].iloc[0]}')
print(f'Sample article: {df["article_id"].iloc[0]}')
