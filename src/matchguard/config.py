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
