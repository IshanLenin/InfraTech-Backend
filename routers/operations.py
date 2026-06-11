from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas.catalog import OperationsAnalyticsResponse
from typing import Optional
from datetime import datetime
from fastapi import Query

# Initialize the modular router
router = APIRouter(
    prefix="/api/v1/admin/analytics/operations",
    tags=["Catalog Performance & Platform Operations"]
)

@router.get("", response_model=OperationsAnalyticsResponse)
def get_operations_analytics(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter up to date")
):
    try:
        
        if start_date and end_date is not None and start_date > end_date:
            raise HTTPException(status_code = 400, detail = "Invalid date range")

        params = {}
        date_filter_sql = ""
        
        if start_date:
            date_filter_sql += " AND created_at >= :start_date"
            params["start_date"] = start_date
        if end_date:
            date_filter_sql += " AND created_at <= :end_date"
            params["end_date"] = end_date

        # 1. Deals Query
        deal_query = f"""
            SELECT 
                COUNT(id) FILTER (WHERE status = true) AS active_deals,
                COUNT(id) FILTER (WHERE status = false) AS inactive_deals,
                COUNT(id) FILTER (WHERE seo_title IS NOT NULL) AS seo_complete,
                COUNT(id) FILTER (WHERE seo_title IS NULL) AS seo_missing
            FROM deal WHERE 1=1 {date_filter_sql}
        """
        deal_res = db.execute(text(deal_query), params).fetchone()

        # 2. Tickets Query
        ticket_query = f"""
            SELECT 
                COUNT(id) AS total_tickets,
                COUNT(id) FILTER (WHERE status = false) AS unresolved,
                COUNT(id) FILTER (WHERE status = true) AS resolved
            FROM tickets WHERE 1=1 {date_filter_sql}
        """
        ticket_res = db.execute(text(ticket_query), params).fetchone()

        # 3. Notifications Query
        notif_query = f"""
            SELECT 
                COUNT(id) AS total_sent,
                COUNT(id) FILTER (WHERE read_status = true) AS total_read,
                COUNT(DISTINCT user_id) AS distinct_users
            FROM user_notifications WHERE 1=1 {date_filter_sql}
        """
        notif_res = db.execute(text(notif_query), params).fetchone()

        # ---------------------------------------------------------
        # 4. THE COMPLEX REWARD RATIO LOGIC
        # ---------------------------------------------------------
        reward_query = f"""
            SELECT 
                COUNT(id) AS successful_rewards
            FROM reward 
            WHERE type IN ('final_reward', 'redeem_cash_back', 'signup_reward', 'refer_reward', 'referral_reward', 'refer_bonus') {date_filter_sql}
        """
        reward_res = db.execute(text(reward_query), params).fetchone()

        # Extract values safely
        total_tickets = ticket_res.total_tickets if ticket_res and ticket_res.total_tickets else 0
        successful_rewards = reward_res.successful_rewards if reward_res and reward_res.successful_rewards else 0
        
        # Calculate the operational friction ratio (Tickets per Reward)
        # We cap it at 4 decimal places just like your original system dump (e.g., 0.1423)
        friction_ratio = round(total_tickets / successful_rewards, 4) if successful_rewards > 0 else 0.0

        # Calculate notification math
        sent = notif_res.total_sent if notif_res and notif_res.total_sent else 0
        read = notif_res.total_read if notif_res and notif_res.total_read else 0
        read_rate = round((read / sent * 100), 2) if sent > 0 else 0.0

        return {
            "catalog_status": {
                "active_deals": deal_res.active_deals if deal_res and deal_res.active_deals else 0,
                "inactive_deals": deal_res.inactive_deals if deal_res and deal_res.inactive_deals else 0,
                "seo_coverage": {
                    "completed": deal_res.seo_complete if deal_res and deal_res.seo_complete else 0,
                    "missing": deal_res.seo_missing if deal_res and deal_res.seo_missing else 0,
                    "partially_filled": 0
                }
            },
            "support_load": {
                "global_metrics": {
                    "total_tickets": total_tickets,
                    "successful_rewards": successful_rewards,
                    "tickets_per_reward_ratio": friction_ratio
                },
                "backlog_aging": [
                    { "backlog_flag": "unresolved_backlog", "ticket_count": ticket_res.unresolved if ticket_res else 0, "avg_days_open": 0.0 },
                    { "backlog_flag": "resolved_cleanly", "ticket_count": ticket_res.resolved if ticket_res else 0, "avg_days_open": 0.0 }
                ]
            },
            "notification_reach": {
                "total_sent": sent,
                "total_read": read,
                "read_rate_percent": read_rate,
                "distinct_users_targeted": notif_res.distinct_users if notif_res and notif_res.distinct_users else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database execution failed: {str(e)}")