from pydantic import BaseModel,Field
from typing import List, Optional

class SEOCoverage(BaseModel):
    completed: int = Field(..., description="Deals with fully optimized meta-attributes")
    missing: int = Field(..., description="Deals lacking search engine indexing markers")
    partially_filled: int = Field(..., description="Deals needing operational data updates")

class CatalogStatus(BaseModel):
    active_deals: int = Field(..., description="Live available retail links")
    inactive_deals: int = Field(..., description="Expired or turned-off partner links")
    seo_coverage: SEOCoverage

class SupportGlobalMetrics(BaseModel):
    total_tickets: int = Field(..., description="Total client interactions registered")
    successful_rewards: int = Field(..., description="Total valid settled reward records logged")
    tickets_per_reward_ratio: float = Field(..., description="Operational systemic friction ratio")

class BacklogAgingEntry(BaseModel):
    backlog_flag: str = Field(..., description="Status classification bucket string")
    ticket_count: int = Field(..., description="Total active items under this designation")
    avg_days_open: float = Field(..., description="Mean resolution latency metric in fractional days")

class SupportLoadSummary(BaseModel):
    global_metrics: SupportGlobalMetrics
    backlog_aging: List[BacklogAgingEntry]

class NotificationReach(BaseModel):
    total_sent: int = Field(..., description="Gross system delivery attempts triggered")
    total_read: int = Field(..., description="Total customer tracking confirmations recorded")
    read_rate_percent: float = Field(..., description="Systemic messaging engagement efficiency")
    distinct_users_targeted: int = Field(..., description="Total base population reach footprint")

class OperationsAnalyticsResponse(BaseModel):
    catalog_status: CatalogStatus
    support_load: SupportLoadSummary
    notification_reach: NotificationReach

class BrandCashbackResponse(BaseModel):
    brand_id: int
    brand_name: str
    category: Optional[str]
    total_cashback_distributed: float = Field(..., description="Sum of completed cashbacks")
    pending_cashback_liability: float = Field(..., description="Sum of pending cashbacks")
    total_transactions_count: int