from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from typing import Any

from matchguard.models import RiskReport


@dataclass(frozen=True)
class ModerationCase:
    case_id: str
    match_id: str
    player_id: str
    severity: str
    risk_score: int
    summary: str
    reasons: list[str]
    recommended_action: str
    timeline: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "match_id": self.match_id,
            "player_id": self.player_id,
            "severity": self.severity,
            "risk_score": self.risk_score,
            "summary": self.summary,
            "reasons": self.reasons,
            "recommended_action": self.recommended_action,
            "timeline": self.timeline,
        }


def build_moderation_case(report: RiskReport) -> ModerationCase:
    reasons = sorted(report.reasons)
    timeline = [
        {
            "event_ts": evidence.event_ts,
            "reason": evidence.reason,
            "detail": evidence.detail,
            "weight": evidence.weight,
        }
        for evidence in sorted(
            report.evidence,
            key=lambda item: (item.event_ts is None, item.event_ts if item.event_ts is not None else 0),
        )
    ]

    return ModerationCase(
        case_id=_case_id(report),
        match_id=report.match_id,
        player_id=report.player_id,
        severity=_severity(report.risk_score),
        risk_score=report.risk_score,
        summary=_summary(report, reasons),
        reasons=reasons,
        recommended_action=report.action,
        timeline=timeline,
    )


def build_moderation_cases(reports: list[RiskReport]) -> list[ModerationCase]:
    return [build_moderation_case(report) for report in reports]


def _case_id(report: RiskReport) -> str:
    raw = f"{report.match_id}:{report.player_id}:{report.risk_score}:{','.join(report.reasons)}"
    return f"case_{sha1(raw.encode('utf-8')).hexdigest()[:12]}"


def _severity(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def _summary(report: RiskReport, reasons: list[str]) -> str:
    reason_text = ", ".join(reason.replace("_", " ") for reason in reasons[:3])
    if len(reasons) > 3:
        reason_text += f", and {len(reasons) - 3} more"
    return f"{report.player_id} scored {report.risk_score}/100 in {report.match_id}: {reason_text}"
