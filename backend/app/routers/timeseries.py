# app/routes/timeseries.py

import os
from fastapi import APIRouter, HTTPException
import pandas as pd

import sys
import os

# add the ml/timeseries folder to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '../../../models/timeseries')))


# Import your existing utilities
from forecasting_utils import _load_forecast_files, aggregate_forecasts
from analytics_part3 import (
    compute_revenue_forecast, compute_stockout_risk,
    classify_trend, compute_monthly_growth_rate,
    assign_product_lifecycle
)
from data_loader import load_data, get_db_engine

OUT_BASE = "data/ml/timeseries/final_xgb"
FORECAST_DIR = os.path.join(OUT_BASE, "forecasts")
EDA_DIR = os.path.join(OUT_BASE, "eda")

timeseries_router = APIRouter()

# ---------------------------
# 1) Load all forecasts
# ---------------------------
@timeseries_router.get("/forecasts/all")
def get_all_forecasts():
    df = _load_forecast_files(FORECAST_DIR)
    if df.empty:
        raise HTTPException(404, "No forecasts found.")
    return df.to_dict(orient="records")


# ---------------------------
# 2) Forecast by ARTICLE
# ---------------------------
@timeseries_router.get("/forecast/article/{article_id}")
def get_article_forecast(article_id: str):
    df = _load_forecast_files(FORECAST_DIR)
    df = df[df["article_id"].astype(str) == str(article_id)]

    if df.empty:
        raise HTTPException(404, "No forecast found for this article.")
    return df.to_dict(orient="records")


# ---------------------------
# 3) Forecast by CATEGORY
# ---------------------------
@timeseries_router.get("/forecast/category/{category_id}")
def get_category_forecast(category_id: int):
    df = _load_forecast_files(FORECAST_DIR)
    df = df[df["category_id"] == category_id]

    if df.empty:
        raise HTTPException(404, "No forecast found for this category.")
    return df.to_dict(orient="records")


# ---------------------------
# 4) Revenue Forecast (Agg)
# ---------------------------
@timeseries_router.get("/analytics/revenue")
def get_revenue_forecast():
    df = _load_forecast_files(FORECAST_DIR)

    if df.empty:
        raise HTTPException(404, "No forecast files found.")

    raw_df = load_data(from_cache=True)
    rev = compute_revenue_forecast(df, raw_df)
    return rev.to_dict(orient="records")


# ---------------------------
# 5) Stockout Risk
# ---------------------------
@timeseries_router.get("/analytics/stockout")
def stockout_risk():
    df = _load_forecast_files(FORECAST_DIR)
    raw_df = load_data(from_cache=True)
    rev = compute_revenue_forecast(df, raw_df)

    result = compute_stockout_risk(rev)
    return result.to_dict(orient="records")


# ---------------------------
# 6) Trend Classification
# ---------------------------
@timeseries_router.get("/analytics/trends")
def get_trends():
    df = _load_forecast_files(FORECAST_DIR)
    raw_df = load_data(from_cache=True)
    rev = compute_revenue_forecast(df, raw_df)

    result = classify_trend(rev)
    return result.to_dict(orient="records")


# ---------------------------
# 7) Monthly Growth Rate
# ---------------------------
@timeseries_router.get("/analytics/monthly_growth")
def get_monthly_growth():
    df = _load_forecast_files(FORECAST_DIR)
    raw_df = load_data(from_cache=True)
    rev = compute_revenue_forecast(df, raw_df)

    monthly = compute_monthly_growth_rate(rev)
    return monthly.to_dict(orient="records")


# ---------------------------
# 8) Product Lifecycle Stages
# ---------------------------
@timeseries_router.get("/analytics/lifecycle")
def lifecycle_stage():
    df = _load_forecast_files(FORECAST_DIR)
    raw_df = load_data(from_cache=True)
    rev = compute_revenue_forecast(df, raw_df)

    result = assign_product_lifecycle(rev)
    return result.to_dict(orient="records")


# ---------------------------
# 9) Weekly + Monthly Aggregations
# ---------------------------
@timeseries_router.get("/analytics/aggregate")
def get_aggregates():
    df = _load_forecast_files(FORECAST_DIR)
    if df.empty:
        raise HTTPException(404, "No forecasts found.")
    weekly, monthly = aggregate_forecasts(df)

    return {
        "weekly": weekly.to_dict(orient="records") if weekly is not None else [],
        "monthly": monthly.to_dict(orient="records") if monthly is not None else []
    }


# ---------------------------
# 10) RUN FULL PIPELINE (OPTIONAL SAFE VERSION)
# ---------------------------
@timeseries_router.post("/pipeline/run")
def run_full_pipeline():
    """
    Runs:
     - load data
     - clean + reindex
     - EDA
     - model training (article + category)
     - forecasting
     - analytics (trends, stockout, lifecycle)
     - aggregations
    """
    try:
        os.system("python ml/timeseries/main_pipeline.py")
        return {"status": "Pipeline executed successfully."}
    except Exception as e:
        raise HTTPException(500, f"Pipeline failed: {e}")
