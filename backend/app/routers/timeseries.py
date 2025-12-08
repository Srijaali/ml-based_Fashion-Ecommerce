"""
Timeseries Endpoints Module

Implements all the required endpoints for the frontend masterplan:
- Forecast Dashboard endpoints
- Analytics Dashboard endpoints
- Aggregated Views endpoints
- Pipeline endpoint
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add the current directory to path to import other modules
sys.path.append(os.path.dirname(__file__))

from forecasting_utils import _load_forecast_files, aggregate_forecasts
from analytics_part3 import (
    compute_revenue_forecast,
    compute_stockout_risk,
    classify_trend,
    compute_monthly_growth_rate,
    assign_product_lifecycle,
    compute_sales_funnel
)
from data_loader import get_db_engine, load_data

# Constants
OUT_BASE = "data/ml/timeseries/final_xgb"
EDA_DIR = os.path.join(OUT_BASE, "eda")
FORECAST_DIR = os.path.join(OUT_BASE, "forecasts")

def check_data_availability():
    """Check if required data directories and files exist"""
    if not os.path.exists(OUT_BASE):
        raise FileNotFoundError(f"ML data directory not found: {OUT_BASE}")
    if not os.path.exists(FORECAST_DIR):
        raise FileNotFoundError(f"Forecast data directory not found: {FORECAST_DIR}")

# ============================================================
# FORECAST DASHBOARD ENDPOINTS
# ============================================================

def get_all_forecasts():
    """
    Get all forecasts for articles/categories.
    
    Endpoint: /forecasts/all
    Returns: List of forecast data for all articles
    """
    try:
        check_data_availability()
        all_fc = _load_forecast_files()
        return all_fc.to_dict('records') if not all_fc.empty else []
    except Exception as e:
        raise Exception(f"Error getting all forecasts: {str(e)}")

def get_article_forecast(article_id):
    """
    Get forecast for a specific article.
    
    Endpoint: /forecast/article/{id}
    Args:
        article_id (str): The article ID
    Returns: List of forecast data for the specified article
    """
    try:
        check_data_availability()
        all_fc = _load_forecast_files()
        if all_fc.empty:
            return []
        
        # Filter for specific article
        article_fc = all_fc[all_fc['article_id'] == article_id]
        return article_fc.to_dict('records') if not article_fc.empty else []
    except Exception as e:
        raise Exception(f"Error getting forecast for article {article_id}: {str(e)}")

def get_category_forecast(category_id):
    """
    Get forecast for a specific category.
    
    Endpoint: /forecast/category/{id}
    Args:
        category_id (str): The category ID
    Returns: List of forecast data for the specified category
    """
    try:
        check_data_availability()
        all_fc = _load_forecast_files()
        if all_fc.empty:
            return []
        
        # Load article data to get category mapping
        try:
            articles_df = load_data(from_cache=True)
            # Filter articles by category
            category_articles = articles_df[articles_df['category_id'] == int(category_id)]['article_id'].tolist()
            
            # Filter forecasts for articles in this category
            category_fc = all_fc[all_fc['article_id'].isin(category_articles)]
            return category_fc.to_dict('records') if not category_fc.empty else []
        except:
            # Fallback if we can't load article data
            return []
    except Exception as e:
        raise Exception(f"Error getting forecast for category {category_id}: {str(e)}")

def get_revenue_analytics():
    """
    Get revenue analytics for forecasts.
    
    Endpoint: /analytics/revenue
    Returns: List of revenue analytics data
    """
    try:
        check_data_availability()
        all_fc = _load_forecast_files()
        if all_fc.empty:
            return []
        
        # Get article data for price information
        try:
            articles_df = load_data(from_cache=True)[['article_id', 'avg_price']].drop_duplicates()
        except:
            articles_df = pd.DataFrame(columns=['article_id', 'avg_price'])
        
        result = compute_revenue_forecast(all_fc, articles_df)
        return result.to_dict('records') if not result.empty else []
    except Exception as e:
        raise Exception(f"Error computing revenue analytics: {str(e)}")

# ============================================================
# ANALYTICS DASHBOARD ENDPOINTS
# ============================================================

def get_stockout_analytics():
    """
    Get stockout risk analytics.
    
    Endpoint: /analytics/stockout
    Returns: List of stockout risk data
    """
    try:
        check_data_availability()
        all_fc = _load_forecast_files()
        if all_fc.empty:
            return []
            
        result = compute_stockout_risk(all_fc)
        return result.to_dict('records') if not result.empty else []
    except Exception as e:
        raise Exception(f"Error computing stockout analytics: {str(e)}")

def get_trend_analytics():
    """
    Get trend classification analytics.
    
    Endpoint: /analytics/trends
    Returns: List of trend classification data
    """
    try:
        check_data_availability()
        all_fc = _load_forecast_files()
        if all_fc.empty:
            return []
            
        result = classify_trend(all_fc)
        return result.to_dict('records') if not result.empty else []
    except Exception as e:
        raise Exception(f"Error computing trend analytics: {str(e)}")

def get_monthly_growth_analytics():
    """
    Get monthly growth rate analytics.
    
    Endpoint: /analytics/monthly_growth
    Returns: List of monthly growth rate data
    """
    try:
        check_data_availability()
        all_fc = _load_forecast_files()
        if all_fc.empty:
            return []
            
        result = compute_monthly_growth_rate(all_fc)
        # Convert period to string for serialization
        if 'month' in result.columns:
            result['month'] = result['month'].astype(str)
        return result.to_dict('records') if not result.empty else []
    except Exception as e:
        raise Exception(f"Error computing monthly growth analytics: {str(e)}")

def get_lifecycle_analytics():
    """
    Get product lifecycle analytics.
    
    Endpoint: /analytics/lifecycle
    Returns: List of product lifecycle data
    """
    try:
        check_data_availability()
        all_fc = _load_forecast_files()
        if all_fc.empty:
            return []
            
        result = assign_product_lifecycle(all_fc)
        return result.to_dict('records') if not result.empty else []
    except Exception as e:
        raise Exception(f"Error computing lifecycle analytics: {str(e)}")

# ============================================================
# AGGREGATED VIEWS ENDPOINTS
# ============================================================

def get_aggregated_analytics(view_type="weekly"):
    """
    Get aggregated forecast analytics.
    
    Endpoint: /analytics/aggregate
    Args:
        view_type (str): Either "weekly" or "monthly"
    Returns: List of aggregated forecast data
    """
    try:
        check_data_availability()
        all_fc = _load_forecast_files()
        if all_fc.empty:
            return []
        
        if view_type == "weekly":
            # Add week_start column
            all_fc["week_start"] = all_fc["date"].dt.to_period("W").apply(lambda r: r.start_time)
            # Group by week and sum predicted sales
            agg_data = all_fc.groupby('week_start')['predicted_sales'].sum().reset_index()
            agg_data = agg_data.rename(columns={'week_start': 'date'})
        elif view_type == "monthly":
            # Add month_start column
            all_fc["month_start"] = all_fc["date"].dt.to_period("M").apply(lambda r: r.start_time)
            # Group by month and sum predicted sales
            agg_data = all_fc.groupby('month_start')['predicted_sales'].sum().reset_index()
            agg_data = agg_data.rename(columns={'month_start': 'date'})
        else:
            # Daily aggregation
            agg_data = all_fc.groupby('date')['predicted_sales'].sum().reset_index()
        
        return agg_data.to_dict('records') if not agg_data.empty else []
    except Exception as e:
        raise Exception(f"Error computing aggregated analytics: {str(e)}")

# ============================================================
# PIPELINE ENDPOINT
# ============================================================

def run_full_pipeline():
    """
    Run the full timeseries pipeline.
    
    Endpoint: /pipeline/run
    Returns: Status message
    """
    try:
        from main_pipeline import main as pipeline_main
        pipeline_main()
        return {
            "status": "success",
            "message": "Timeseries pipeline completed successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error running pipeline: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# ============================================================
# ADDITIONAL HELPER ENDPOINTS
# ============================================================

def get_forecast_by_date_range(start_date, end_date):
    """
    Get forecasts within a specific date range.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    Returns: List of forecast data within the date range
    """
    try:
        check_data_availability()
        all_fc = _load_forecast_files()
        if all_fc.empty:
            return []
        
        # Convert string dates to datetime
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Filter by date range
        filtered_fc = all_fc[(all_fc['date'] >= start_dt) & (all_fc['date'] <= end_dt)]
        return filtered_fc.to_dict('records') if not filtered_fc.empty else []
    except Exception as e:
        raise Exception(f"Error getting forecasts by date range: {str(e)}")

def get_forecast_horizon(days=30):
    """
    Get forecasts for a specific horizon (next N days).
    
    Args:
        days (int): Number of days into the future
    Returns: List of forecast data for the specified horizon
    """
    try:
        check_data_availability()
        all_fc = _load_forecast_files()
        if all_fc.empty:
            return []
        
        # Get forecasts from today onwards for the specified number of days
        today = pd.Timestamp.now().normalize()
        end_date = today + timedelta(days=days)
        
        # Filter by date range
        filtered_fc = all_fc[(all_fc['date'] >= today) & (all_fc['date'] <= end_date)]
        return filtered_fc.to_dict('records') if not filtered_fc.empty else []
    except Exception as e:
        raise Exception(f"Error getting forecast horizon: {str(e)}")

# Export all endpoint functions
__all__ = [
    # Forecast Dashboard endpoints
    'get_all_forecasts',
    'get_article_forecast',
    'get_category_forecast',
    'get_revenue_analytics',
    
    # Analytics Dashboard endpoints
    'get_stockout_analytics',
    'get_trend_analytics',
    'get_monthly_growth_analytics',
    'get_lifecycle_analytics',
    
    # Aggregated Views endpoints
    'get_aggregated_analytics',
    
    # Pipeline endpoint
    'run_full_pipeline',
    
    # Additional helper endpoints
    'get_forecast_by_date_range',
    'get_forecast_horizon'
]
