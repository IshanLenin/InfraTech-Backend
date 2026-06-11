from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas.engagement import ConversionAnalyticsResponse
from datetime import datetime
from typing import Optional
from fastapi import Query

router = APIRouter(
    prefix="/api/v1/admin/analytics/conversions",
    tags=["Engagement & Conversion Funnel"]
)

@router.get("", response_model=ConversionAnalyticsResponse)
def get_conversion_analytics(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter up to date")
):
    try:

        if start_date and end_date is not None and start_date > end_date:
            raise HTTPException(status_code = 400, detail = "Invalid date range")
        
        base_query = """
            SELECT 
                COUNT(id) FILTER (WHERE type = 'redirect_reward') AS total_redirects,
                COUNT(id) FILTER (WHERE type = 'pending_reward') AS total_pending,
                COUNT(id) FILTER (WHERE type = 'final_reward') AS total_final,
                COUNT(id) FILTER (WHERE receipt_uploaded = TRUE) AS total_receipts
            FROM reward
            WHERE 1=1
        """
        
        params = {}
        if start_date:
            base_query += " AND created_at >= :start_date"
            params["start_date"] = start_date
        if end_date:
            base_query += " AND created_at <= :end_date"
            params["end_date"] = end_date

        result = db.execute(text(base_query), params).fetchone()

        # Safely extract values
        redirects = result.total_redirects if result and result.total_redirects else 0
        pending = result.total_pending if result and result.total_pending else 0
        final = result.total_final if result and result.total_final else 0
        receipts = result.total_receipts if result and result.total_receipts else 0

        # Calculate dynamic drop-offs
        pending_drop_off = round(((redirects - pending) / redirects * 100), 2) if redirects > 0 else 0.0
        final_drop_off = round(((pending - final) / pending * 100), 2) if pending > 0 else 0.0
        upload_rate = round((receipts / final * 100), 2) if final > 0 else 0.0

        return {
            "traffic_engagement": {
                "total_redirects": redirects,
                "total_deal_clicks": redirects # Assuming deal clicks map 1:1 with redirects for now
            },
            "conversion_funnel": [
                { "stage": "Redirects", "count": redirects, "drop_off_percent": 0.0 },
                { "stage": "Pending Rewards", "count": pending, "drop_off_percent": pending_drop_off },
                { "stage": "Final Rewards", "count": final, "drop_off_percent": final_drop_off }
            ],
            "receipt_metrics": {
                "total_rewards_with_receipt": receipts,
                "upload_rate_percent": upload_rate
            },
            "active_users_time_series": [] # Time series aggregation to be built separately
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database execution failed: {str(e)}")