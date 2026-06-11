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
    end_date: Optional[datetime] = Query(None, description="Filter up to date (YYYY-MM-DD)")
):
    try:
        # We fetch all the metrics in a single database hit for maximum performance
        base_query = """
            SELECT 
                COUNT(id) AS total_users,
                COUNT(id) FILTER (WHERE status = 'active') AS active_users,
                COUNT(id) FILTER (WHERE status = 'inactive') AS inactive_users,
                COUNT(id) FILTER (WHERE is_verified = TRUE) AS verified_users,
                COUNT(id) FILTER (WHERE referrer_id IS NOT NULL) AS referred_users,
                COUNT(email) AS total_emails
            FROM users
            WHERE 1=1
        """
        
        # 3. Append date filters safely if the user provided them
        params = {}
        if start_date:
            base_query += " AND created_at >= :start_date"
            params["start_date"] = start_date
        if end_date:
            base_query += " AND created_at <= :end_date"
            params["end_date"] = end_date

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
                "growth_metric": {
                    "june_mom_percent": 0.0, 
                    "may_mom_percent": 0.0,
                    "april_mom_percent": 0.0
                },
                "historical_data": [] # Placeholder until we write the cohort aggregation query
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