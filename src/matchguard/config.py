from __future__ import annotations

import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScoringConfig:
    max_speed_units_per_second: float = 13.0
    aim_snap_degrees: float = 70.0
    aim_snap_window_seconds: float = 0.25
    min_shots_for_hit_rate: int = 10
    abnormal_hit_rate: float = 0.85
    min_hits_for_headshot_rate: int = 6
    abnormal_headshot_rate: float = 0.75
    hidden_hit_count: int = 3
    report_weight_per_reporter: int = 5
    max_report_weight: int = 20

    def __post_init__(self) -> None:
        _require_positive_number("max_speed_units_per_second", self.max_speed_units_per_second)
        _require_positive_number("aim_snap_degrees", self.aim_snap_degrees)
        _require_positive_number("aim_snap_window_seconds", self.aim_snap_window_seconds)
        _require_positive_int("min_shots_for_hit_rate", self.min_shots_for_hit_rate)
        _require_probability("abnormal_hit_rate", self.abnormal_hit_rate)
        _require_positive_int("min_hits_for_headshot_rate", self.min_hits_for_headshot_rate)
        _require_probability("abnormal_headshot_rate", self.abnormal_headshot_rate)
        _require_positive_int("hidden_hit_count", self.hidden_hit_count)
        _require_non_negative_int("report_weight_per_reporter", self.report_weight_per_reporter)
        _require_non_negative_int("max_report_weight", self.max_report_weight)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ScoringConfig":
        allowed = {field.name for field in fields(cls)}
        unknown = sorted(set(raw) - allowed)
        if unknown:
            raise ValueError(f"unknown scoring config fields: {', '.join(unknown)}")
        return cls(**{key: raw[key] for key in raw if key in allowed})

    @classmethod
    def from_path(cls, path: Path) -> "ScoringConfig":
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict):
            raise ValueError("scoring config must be a JSON object")
        return cls.from_dict(raw)


def _require_positive_number(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be a positive number")


def _require_probability(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1")


def _require_positive_int(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _require_non_negative_int(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
