from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas.financials import EconomicsAnalyticsResponse
from schemas.catalog import BrandCashbackResponse
from datetime import datetime
from typing import Optional, List
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
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            raise HTTPException(status_code=400, detail=f"Invalid amount range") 
        if start_date is not None and end_date is not None and start_date > end_date:
            raise HTTPException(status_code=400, detail=f"Invalid date range")

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
            if reward_type in ["pending_reward", "final_reward", "redeem_cash_back", "rejected_reward"]:
                ledger_query += " AND type = :reward_type"
                params["reward_type"] = reward_type
            else:
                raise HTTPException(status_code = 400, detail = f"Invalid reward type: {reward_type}")
        
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

@router.get("/brands/search", response_model=List[BrandCashbackResponse], tags=["Brand Financial Performance"])
def search_brand_cashback(
    db: Session = Depends(get_db),
    query: Optional[str] = Query(None, description="Search brand by name (e.g., 'Amazon')"),
    brand_id: Optional[int] = Query(None, description="Filter directly by brand ID")
):
    try:
        params = {}
        # 1. Base SQL leveraging relational JOINs across the catalog and ledger
        sql = """
            SELECT 
                b.id AS brand_id,
                b.name AS brand_name,
                b.category,
                COALESCE(SUM(r.amount) FILTER (WHERE r.type IN ('final_reward', 'redeem_cash_back')), 0.00) AS total_cashback,
                COALESCE(SUM(r.amount) FILTER (WHERE r.type = 'pending_reward'), 0.00) AS pending_cashback,
                COUNT(r.id) AS transaction_count
            FROM brands b
            LEFT JOIN deal d ON b.id = d.brand_id
            LEFT JOIN reward r ON d.id = r.deal_id
            WHERE 1=1
        """
        
        # 2. Inject dynamic search parameters safely
        if brand_id:
            sql += " AND b.id = :brand_id"
            params["brand_id"] = brand_id
        if query:
            sql += " AND b.name ILIKE :query"
            params["query"] = f"%{query}%"
            
        sql += " GROUP BY b.id, b.name, b.category ORDER BY total_cashback DESC;"
        
        results = db.execute(text(sql), params).fetchall()
        
        # 3. Format the flat database rows into the validated schema array
        return [
            {
                "brand_id": row.brand_id,
                "brand_name": row.brand_name,
                "category": row.category,
                "total_cashback_distributed": float(row.total_cashback),
                "pending_cashback_liability": float(row.pending_cashback),
                "total_transactions_count": row.transaction_count
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database compilation failed: {str(e)}")