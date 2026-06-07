from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MatchEvent:
    match_id: str
    player_id: str
    type: str
    ts: float
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "MatchEvent":
        required = ("match_id", "player_id", "type", "ts")
        missing = [key for key in required if key not in raw]
        if missing:
            raise ValueError(f"event is missing required fields: {', '.join(missing)}")

        payload = {key: value for key, value in raw.items() if key not in required}
        return cls(
            match_id=str(raw["match_id"]),
            player_id=str(raw["player_id"]),
            type=str(raw["type"]),
            ts=float(raw["ts"]),
            payload=payload,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "match_id": self.match_id,
            "player_id": self.player_id,
            "type": self.type,
            "ts": self.ts,
            **self.payload,
        }


@dataclass(frozen=True)
class Evidence:
    reason: str
    weight: int
    event_ts: float | None
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "reason": self.reason,
            "weight": self.weight,
            "event_ts": self.event_ts,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class RiskReport:
    match_id: str
    player_id: str
    risk_score: int
    reasons: list[str]
    evidence: list[Evidence]
    action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "match_id": self.match_id,
            "player_id": self.player_id,
            "risk_score": self.risk_score,
            "reasons": self.reasons,
            "evidence": [item.to_dict() for item in self.evidence],
            "action": self.action,
        }
