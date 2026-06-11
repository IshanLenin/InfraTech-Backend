from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas.financials import EconomicsAnalyticsResponse
from datetime import datetime
from typing import Optional
from fastapi import Query

router = APIRouter(
    prefix="/api/v1/admin/analytics/economics",
    tags=["Financials & Unit Economics"]
)

@router.get("", response_model=EconomicsAnalyticsResponse)
def get_economics_analytics(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter up to date"),
    deal_id: Optional[int] = Query(None, description="Filter by deal ID"),
    min_amount: Optional[float] = Query(None, description = "Filter by minimum reward amount"),
    max_amount: Optional[float] = Query(None, description = "Filter by maximum reward amount"),
    reward_type: Optional[str] = Query(None, description = "Filter by reward type")
):
    try:
        # Ledger Query with Date Filters
        ledger_query = """
            SELECT 
                COUNT(id) FILTER (WHERE type = 'pending_reward') AS pending,
                COUNT(id) FILTER (WHERE type IN ('final_reward', 'redeem_cash_back')) AS completed,
                COUNT(id) FILTER (WHERE type = 'rejected_reward') AS cancelled
            FROM reward
            WHERE 1=1
        """
        params = {}
        if start_date:
            ledger_query += " AND created_at >= :start_date"
            params["start_date"] = start_date
        if end_date:
            ledger_query += " AND created_at <= :end_date"
            params["end_date"] = end_date
        if deal_id:
            ledger_query += " AND deal_id = :deal_id"
            params["deal_id"] = deal_id
        if min_amount:
            ledger_query += " AND amount >= :min_amount"
            params["min_amount"] = min_amount
        if max_amount:
            ledger_query += " AND amount <= :max_amount"
            params["max_amount"] = max_amount
        if reward_type:
            ledger_query += " AND type = :reward_type"
            params["reward_type"] = reward_type

        ledger_result = db.execute(text(ledger_query), params).fetchone()

        # Global Loyalty Query (Usually Unfiltered by date to show total running liability)
        loyalty_query = text("""
            SELECT 
                SUM(pp_points) AS issued,
                SUM(latest_pp_point) AS balance
            FROM users;
        """)
        loyalty_result = db.execute(loyalty_query).fetchone()

        return {
            "cashback_cases": {
                "pending": ledger_result.pending if ledger_result and ledger_result.pending else 0,
                "completed": ledger_result.completed if ledger_result and ledger_result.completed else 0,
                "cancelled": ledger_result.cancelled if ledger_result and ledger_result.cancelled else 0
            },
            "loyalty_currency": {
                "total_pp_points_issued": loyalty_result.issued if loyalty_result and loyalty_result.issued else 0,
                "total_latest_pp_points_balance": loyalty_result.balance if loyalty_result and loyalty_result.balance else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database execution failed: {str(e)}")