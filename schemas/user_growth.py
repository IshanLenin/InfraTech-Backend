from pydantic import BaseModel, Field
from typing import List

class GrowthMetric(BaseModel):
    june_mom_percent: float = Field(..., description="June MoM Percentage")
    may_mom_percent: float = Field(..., description="May MoM Percentage")
    april_mom_percent: float = Field(..., description="April MoM Percentage")

class HistoricalSignUp(BaseModel):
    period: str = Field(..., description="Period")
    users_onboarded: int = Field(..., description="Number of users onboarded")

class UserBaseSummary(BaseModel):
    cumulative_total: int = Field(..., description="Cumulative Total")
    growth_metric: GrowthMetric = Field(..., description="Growth Metric")
    historical_data: List[HistoricalSignUp] = Field(..., description="Historical Data")

class StatusDistribution(BaseModel):
    verified: int = Field(..., description="Count of fully verified user accounts")
    unverified: int = Field(..., description="Count of unverified user accounts")
    active: int = Field(..., description="Count of users flagged as active")
    inactive: int = Field(..., description="Count of users flagged as inactive")

class EmailCapture(BaseModel):
    total_emails:int = Field(..., description="Total emails collected")
    email_conversion_rate: float = Field(..., description="Email Conversion Rate")

class AcquisitionSummary(BaseModel):
    organic: int = Field(..., description="Signups without a tracking referral code")
    referred: int = Field(..., description="Signups triggered via a referral code invitation")
    email_capture: EmailCapture

class UserAnalyticsResponse(BaseModel):
    user_base: UserBaseSummary
    status_distribution: StatusDistribution
    acquisition: AcquisitionSummary




    