from pydantic import Field,BaseModel
from typing import List

class NetworkSummary(BaseModel):
    distinct_active_referrers: int = Field(..., description="Count of unique users who have successfully invited others")

class ReferrerLeaderboardEntry(BaseModel):
    referrer_id: str = Field(..., description="The uniquely identifiable referral code string")
    total_invites: int = Field(..., description="Total successful signups driven by this instrument")

class ReferralAnalyticsResponse(BaseModel):
    network_summary: NetworkSummary
    top_referrers_leaderboard: List[ReferrerLeaderboardEntry]