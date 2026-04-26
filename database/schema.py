from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class SupplierKPI(BaseModel):
    supplier_name: str
    country: str
    total_orders: int
    otd_rate: float
    avg_lead_time_days: float
    lead_time_std: float
    defect_rate: float
    total_quantity: int
    order_volume: float
    concentration_pct: float


class SentimentScore(BaseModel):
    supplier_name: str
    headline_count: int
    positive_pct: float
    neutral_pct: float
    negative_pct: float
    sentiment_risk_score: float


class RiskScore(BaseModel):
    supplier_name: str
    country: str
    otd_risk: float
    ltv_risk: float
    defect_risk: float
    sentiment_risk: float
    geo_risk: float
    concentration_risk: float
    composite_score: float
    tier: Literal["low", "medium", "high", "critical"]


class SupplierAlert(BaseModel):
    supplier_name: str
    alert_type: str
    severity: str
    message: str
    triggered_at: datetime = None

    def model_post_init(self, __context):
        if self.triggered_at is None:
            object.__setattr__(self, "triggered_at", datetime.utcnow())


class SupplierBrief(BaseModel):
    supplier_name: str
    composite_score: float
    tier: Literal["low", "medium", "high", "critical"]
    brief_text: str
    generated_at: datetime = None

    def model_post_init(self, __context):
        if self.generated_at is None:
            object.__setattr__(self, "generated_at", datetime.utcnow())
