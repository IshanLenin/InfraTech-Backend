from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas.referrals import ReferralAnalyticsResponse
from typing import Optional
from datetime import datetime
from fastapi import Query



router = APIRouter(
    prefix="/api/v1/admin/analytics/referrals",
    tags=["Viral Growth & Referrals"]
)

@router.get("", response_model=ReferralAnalyticsResponse)
def get_referral_analytics(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter up to date")
):
    try:

        if start_date and end_date is not None and start_date > end_date:
            raise HTTPException(status_code = 400, detail = "Invalid date range")
            
        referral_query = """
            SELECT 
                referrer_id AS refer_code, 
                COUNT(*) AS total_invites 
            FROM users 
            WHERE referrer_id IS NOT NULL 
        """
        
        params = {}
        if start_date:
            referral_query += " AND created_at >= :start_date"
            params["start_date"] = start_date
        if end_date:
            referral_query += " AND created_at <= :end_date"
            params["end_date"] = end_date

        referral_query += " GROUP BY referrer_id ORDER BY total_invites DESC LIMIT 10;"

        # Execute and fetch all top referrers
        results = db.execute(text(referral_query), params).fetchall()

        # Format results for Pydantic
        leaderboard = [
            {"referrer_id": row.refer_code, "total_invites": row.total_invites} 
            for row in results
        ]

        # Calculate distinct referrers in this timeframe
        distinct_count = len(leaderboard) # Simplified for current leaderboard limit

        return {
            "network_summary": {
                "distinct_active_referrers": distinct_count
            },
            "top_referrers_leaderboard": leaderboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database execution failed: {str(e)}")