from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


PriorityLevel = Literal["critical", "high", "moderate", "watch"]
BriefingStatus = Literal["stable", "needs-attention", "executive-visible"]


class Signal(BaseModel):
    signal_id: str
    domain: Literal["revenue", "growth", "ops", "security", "ai", "customer"]
    title: str
    metric: str
    current_value: float
    previous_value: float
    target_value: float
    impact_weight: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    owner: str
    due_in_days: int
    note: str


class BriefingInput(BaseModel):
    briefing_id: str
    account_name: str
    audience: Literal["board", "executive", "operating-review"]
    time_horizon: Literal["weekly", "monthly", "quarterly"]
    signals: list[Signal]


class BriefingSummary(BaseModel):
    briefing_id: str
    account_name: str
    audience: str
    status: BriefingStatus
    composite_score: int
    risk_rank: int
    headline: str


class PriorityAction(BaseModel):
    title: str
    owner: str
    priority: PriorityLevel
    due_in_days: int
    rationale: str


class AnalysisResponse(BaseModel):
    status: BriefingStatus
    score: int
    headline: str
    why_it_matters: list[str]
    recommended_next_actions: list[PriorityAction]


class NarrativeResponse(BaseModel):
    executive_summary: str
    shifts_to_watch: list[str]
    opportunity_statement: str
    risk_statement: str


class DashboardSummary(BaseModel):
    briefings: int
    signals: int
    executive_visible_items: int
    average_confidence: float

