from pydantic import BaseModel, Field
from typing import List


class TrafficEngagement(BaseModel):
    total_redirects: int = Field(..., description="Total out-bound tracking link clicks")
    total_deal_clicks: int = Field(..., description="Total raw content interaction events")

class FunnelStage(BaseModel):
    stage: str = Field(..., description="Name of the conversion funnel tier")
    count: int = Field(..., description="Volume of records reaching this state")
    drop_off_percent: float = Field(..., description="Drop-off percentage from the prior tier")

class ReceiptMetrics(BaseModel):
    total_rewards_with_receipt: int = Field(..., description="Count of rewards anchored to a receipt image")
    upload_rate_percent: float = Field(..., description="Percentage rate of receipts uploaded per click")

class ActiveUsersTimeSeries(BaseModel):
    period: str = Field(..., description="Dynamic date-range window identifier")
    count: int = Field(..., description="Distinct user activity count within this window")

class ConversionAnalyticsResponse(BaseModel):
    traffic_engagement: TrafficEngagement
    conversion_funnel: List[FunnelStage]
    receipt_metrics: ReceiptMetrics
    active_users_time_series: List[ActiveUsersTimeSeries]