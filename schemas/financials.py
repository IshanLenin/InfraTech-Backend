from pydantic import BaseModel, Field

class CashbackCases(BaseModel):
    pending: int = Field(..., description="Unsettled ledger items tracking pipeline commissions")
    completed: int = Field(..., description="Settled transactions ready for wallet withdrawal")
    cancelled: int = Field(..., description="Rejection transactions failed via merchant audit")

class LoyaltyCurrency(BaseModel):
    total_pp_points_issued: int = Field(..., description="Total historic loyalty currency created")
    total_latest_pp_points_balance: int = Field(..., description="Current running balance of active loyalty points")

class EconomicsAnalyticsResponse(BaseModel):
    cashback_cases: CashbackCases
    loyalty_currency: LoyaltyCurrency