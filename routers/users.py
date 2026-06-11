from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime
from database import get_db
from schemas.user_growth import UserAnalyticsResponse

router = APIRouter(
    prefix="/api/v1/admin/analytics/users",
    tags=["User Growth & Profile Analytics"]
)

@router.get("", response_model=UserAnalyticsResponse)
def get_user_analytics(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Filter up to date (YYYY-MM-DD)"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    account_status: Optional[bool] = Query(None, description="Filter by account status")
):
    try:
        
        if start_date and end_date is not None and start_date > end_date:
            raise HTTPException(status_code = 400, detail="Invalid date range")
        
        params={}
        date_filter_sql = ""

         # We fetch all the metrics in a single database hit for maximum performance
        base_query = """
            SELECT 
                COUNT(id) AS total_users,
                COUNT(id) FILTER (WHERE status = 'true') AS active_users,
                COUNT(id) FILTER (WHERE status = 'false') AS inactive_users,
                COUNT(id) FILTER (WHERE is_verified = TRUE) AS verified_users,
                COUNT(id) FILTER (WHERE referrer_id IS NOT NULL) AS referred_users,
                COUNT(email) AS total_emails
                FROM users
            WHERE 1=1
        """
        
        # 3. Append date filters safely if the user provided them
        if start_date:
            base_query += " AND created_at >= :start_date"
            params["start_date"] = start_date
        if end_date:
            base_query += " AND created_at <= :end_date"
            params["end_date"] = end_date
        
        if is_verified is not True:
            base_query += " AND is_verified = False"
        
        if account_status:
            base_query += " AND status = :account_status"
            params["account_status"] = account_status

        time_series_query = f"""
            WITH monthly_stats AS (
                SELECT 
                    DATE_TRUNC('month', created_at) AS active_month,
                    COUNT(id) AS new_users
                FROM users
                WHERE 1=1 {date_filter_sql if 'date_filter_sql' in locals() else ""}
                GROUP BY DATE_TRUNC('month', created_at)
            ),
            growth_calc AS (
                SELECT 
                    active_month,
                    new_users,
                    LAG(new_users) OVER (ORDER BY active_month ASC) AS prev_month_users
                FROM monthly_stats
            )
            SELECT 
                active_month,
                new_users,
                CASE 
                    WHEN prev_month_users IS NULL OR prev_month_users = 0 THEN 0.0
                    ELSE ROUND(((new_users - prev_month_users)::numeric / prev_month_users) * 100, 2)
                END AS mom_growth
            FROM growth_calc
            ORDER BY active_month DESC
            LIMIT 6;
        """
        
        ts_results = db.execute(text(time_series_query), params).fetchall()

        # Parse the results into the exact lists and dictionaries Pydantic expects
        historical_buckets = []
        growth_metrics_dict = {"june_mom_percent": 0.0, "may_mom_percent": 0.0, "april_mom_percent": 0.0}
        
        for idx, row in enumerate(ts_results):
            month_label = row.active_month.strftime("%b %Y") if row.active_month else "Unknown"
            historical_buckets.append({"period": month_label, "users_onboarded": row.new_users})

            if idx == 0: growth_metrics_dict["june_mom_percent"] = float(row.mom_growth)
            elif idx == 1: growth_metrics_dict["may_mom_percent"] = float(row.mom_growth)
            elif idx == 2: growth_metrics_dict["april_mom_percent"] = float(row.mom_growth)

        # Execute with safely bound parameters
        result = db.execute(text(base_query), params).fetchone()

        # Handle division by zero for the conversion rate
        total = result.total_users if result and result.total_users > 0 else 1
        total_emails = result.total_emails if result else 0
        conversion_rate = round((total_emails / total) * 100, 2)
        organic_users = total - (result.referred_users if result else 0)

        # 4. Map the live database results to your Pydantic schema
        return {
            "user_base": {
                "cumulative_total": result.total_users if result else 0,
                "growth_metric": growth_metrics_dict,         
                "historical_data": historical_buckets       
            },
            "status_distribution": {
                "verified": result.verified_users if result else 0,
                "unverified": (result.total_users - result.verified_users) if result else 0,
                "active": result.active_users if result else 0,
                "inactive": result.inactive_users if result else 0
            },
            "acquisition": {
                "organic": organic_users,
                "referred": result.referred_users if result else 0,
                "email_capture": {
                    "total_emails": total_emails,
                    "email_conversion_rate": conversion_rate
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database execution failed: {str(e)}")