from fastapi import APIRouter, HTTPException

from app.models import AnalysisResponse, BriefingInput, BriefingSummary, DashboardSummary, NarrativeResponse
from app.sample_data import SAMPLE_BRIEFINGS
from app.services.briefing_engine import (
    build_analysis,
    build_briefing_summary,
    build_narrative,
    build_summary,
)

router = APIRouter(prefix="/api", tags=["briefings"])


@router.get("/briefings", response_model=list[BriefingSummary])
def list_briefings() -> list[BriefingSummary]:
    return [build_briefing_summary(item) for item in SAMPLE_BRIEFINGS]


@router.get("/briefings/{briefing_id}", response_model=BriefingInput)
def get_briefing(briefing_id: str) -> BriefingInput:
    for briefing in SAMPLE_BRIEFINGS:
        if briefing.briefing_id == briefing_id:
            return briefing
    raise HTTPException(status_code=404, detail="Briefing not found")


@router.get("/signals")
def list_signals() -> list[dict]:
    return [signal.model_dump() for briefing in SAMPLE_BRIEFINGS for signal in briefing.signals]


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary() -> DashboardSummary:
    return build_summary(SAMPLE_BRIEFINGS)


@router.post("/analyze/briefing", response_model=AnalysisResponse)
def analyze_briefing(payload: BriefingInput) -> AnalysisResponse:
    return build_analysis(payload)


@router.post("/analyze/narrative", response_model=NarrativeResponse)
def analyze_narrative(payload: BriefingInput) -> NarrativeResponse:
    return build_narrative(payload)


@router.post("/analyze/priorities", response_model=AnalysisResponse)
def analyze_priorities(payload: BriefingInput) -> AnalysisResponse:
    return build_analysis(payload)

