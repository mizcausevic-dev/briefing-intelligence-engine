from __future__ import annotations

import math

import pandas as pd

from app.models import (
    AnalysisResponse,
    BriefingInput,
    BriefingSummary,
    DashboardSummary,
    NarrativeResponse,
    PriorityAction,
)


def _signals_frame(briefing: BriefingInput) -> pd.DataFrame:
    frame = pd.DataFrame([signal.model_dump() for signal in briefing.signals])
    frame["delta"] = frame["current_value"] - frame["previous_value"]
    frame["gap_to_target"] = frame["target_value"] - frame["current_value"]
    frame["urgency"] = frame["impact_weight"] * (1 + (14 - frame["due_in_days"]).clip(lower=0) / 14)
    frame["risk_pressure"] = frame["urgency"] * (1 - frame["confidence"] * 0.35)
    return frame


def _score_briefing(frame: pd.DataFrame) -> int:
    pressure = frame["risk_pressure"].sum() * 18
    variance = frame["gap_to_target"].abs().sum() * 1.7
    score = max(0, min(100, int(round(100 - pressure - variance))))
    return score


def _status_from_score(score: int) -> str:
    if score <= 45:
        return "executive-visible"
    if score <= 70:
        return "needs-attention"
    return "stable"


def _headline(briefing: BriefingInput, frame: pd.DataFrame, score: int) -> str:
    most_pressured = frame.sort_values("risk_pressure", ascending=False).iloc[0]
    status = _status_from_score(score)
    if status == "executive-visible":
        return (
            f"{briefing.account_name} needs immediate coordination around "
            f"{most_pressured['title'].lower()}."
        )
    if status == "needs-attention":
        return (
            f"{briefing.account_name} is still recoverable, but "
            f"{most_pressured['title'].lower()} should lead the next operating review."
        )
    return (
        f"{briefing.account_name} is stable overall, with the clearest upside in "
        f"{most_pressured['title'].lower()}."
    )


def build_analysis(briefing: BriefingInput) -> AnalysisResponse:
    frame = _signals_frame(briefing)
    score = _score_briefing(frame)
    status = _status_from_score(score)
    top_rows = frame.sort_values("risk_pressure", ascending=False).head(3)

    why_it_matters = [
        f"{row.title} is off target by {abs(row.gap_to_target):.1f} on {row.metric}."
        for row in top_rows.itertuples()
    ]

    recommended_next_actions = [
        PriorityAction(
            title=f"Stabilize {row.title.lower()}",
            owner=row.owner,
            priority="critical" if index == 0 and score < 50 else "high" if index < 2 else "moderate",
            due_in_days=max(1, int(row.due_in_days)),
            rationale=(
                f"High weighted pressure driven by {row.metric}, confidence {row.confidence:.0%}, "
                f"and deadline pressure."
            ),
        )
        for index, row in enumerate(top_rows.itertuples())
    ]

    return AnalysisResponse(
        status=status,
        score=score,
        headline=_headline(briefing, frame, score),
        why_it_matters=why_it_matters,
        recommended_next_actions=recommended_next_actions,
    )


def build_narrative(briefing: BriefingInput) -> NarrativeResponse:
    frame = _signals_frame(briefing).sort_values("risk_pressure", ascending=False)
    top = frame.iloc[0]
    strongest = frame.sort_values("delta", ascending=False).iloc[0]
    weakest = frame.sort_values("delta").iloc[0]

    return NarrativeResponse(
        executive_summary=(
            f"{briefing.account_name} has a mixed operating picture: "
            f"{strongest['title'].lower()} is improving, while {top['title'].lower()} "
            f"is now the clearest coordination risk."
        ),
        shifts_to_watch=[
            f"{row.title} with confidence {row.confidence:.0%} and deadline in {int(row.due_in_days)} days."
            for row in frame.head(3).itertuples()
        ],
        opportunity_statement=(
            f"Preserve momentum around {strongest['title'].lower()} and convert that signal "
            "into a visible operating win."
        ),
        risk_statement=(
            f"If {weakest['title'].lower()} continues to deteriorate, the next executive review "
            "will likely shift from optimization into containment."
        ),
    )


def build_summary(briefings: list[BriefingInput]) -> DashboardSummary:
    signal_count = sum(len(item.signals) for item in briefings)
    scores = [build_analysis(item) for item in briefings]
    avg_confidence = round(
        float(
            pd.DataFrame(
                [signal.model_dump() for briefing in briefings for signal in briefing.signals]
            )["confidence"].mean()
        ),
        2,
    )
    return DashboardSummary(
        briefings=len(briefings),
        signals=signal_count,
        executive_visible_items=sum(1 for item in scores if item.status == "executive-visible"),
        average_confidence=avg_confidence,
    )


def build_briefing_summary(briefing: BriefingInput) -> BriefingSummary:
    analysis = build_analysis(briefing)
    risk_rank = max(1, min(10, int(math.ceil((100 - analysis.score) / 10))))
    return BriefingSummary(
        briefing_id=briefing.briefing_id,
        account_name=briefing.account_name,
        audience=briefing.audience,
        status=analysis.status,
        composite_score=analysis.score,
        risk_rank=risk_rank,
        headline=analysis.headline,
    )

