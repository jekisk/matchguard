from __future__ import annotations

from collections import defaultdict
from math import sqrt
from typing import Iterable

from matchguard.models import Evidence, MatchEvent, RiskReport


class RiskScorer:
    """Rule-based scorer for early moderation workflows.

    The first version is intentionally explainable. Projects can tune thresholds
    per game mode before replacing or augmenting rules with learned models.
    """

    def __init__(
        self,
        max_speed_units_per_second: float = 13.0,
        aim_snap_degrees: float = 70.0,
        aim_snap_window_seconds: float = 0.25,
    ) -> None:
        self.max_speed = max_speed_units_per_second
        self.aim_snap_degrees = aim_snap_degrees
        self.aim_snap_window = aim_snap_window_seconds

    def analyze(self, events: Iterable[MatchEvent]) -> list[RiskReport]:
        grouped: dict[tuple[str, str], list[MatchEvent]] = defaultdict(list)
        for event in events:
            grouped[(event.match_id, event.player_id)].append(event)

        reports = []
        for (match_id, player_id), player_events in sorted(grouped.items()):
            evidence = self._score_player(sorted(player_events, key=lambda event: event.ts))
            if not evidence:
                continue

            score = min(100, sum(item.weight for item in evidence))
            reasons = sorted({item.reason for item in evidence})
            reports.append(
                RiskReport(
                    match_id=match_id,
                    player_id=player_id,
                    risk_score=score,
                    reasons=reasons,
                    evidence=evidence,
                    action=self._action_for_score(score),
                )
            )
        return sorted(reports, key=lambda report: report.risk_score, reverse=True)

    def _score_player(self, events: list[MatchEvent]) -> list[Evidence]:
        evidence: list[Evidence] = []
        evidence.extend(self._movement_speed_evidence(events))
        evidence.extend(self._aim_snap_evidence(events))
        evidence.extend(self._combat_ratio_evidence(events))
        evidence.extend(self._report_evidence(events))
        return evidence

    def _movement_speed_evidence(self, events: list[MatchEvent]) -> list[Evidence]:
        evidence = []
        movement = [event for event in events if event.type == "movement"]
        for previous, current in zip(movement, movement[1:]):
            previous_pos = _position(previous)
            current_pos = _position(current)
            if previous_pos is None or current_pos is None:
                continue

            elapsed = current.ts - previous.ts
            if elapsed <= 0:
                continue

            speed = _distance(previous_pos, current_pos) / elapsed
            if speed > self.max_speed:
                evidence.append(
                    Evidence(
                        reason="abnormal_movement_speed",
                        weight=25,
                        event_ts=current.ts,
                        detail=f"speed {speed:.2f} exceeds threshold {self.max_speed:.2f}",
                    )
                )
        return evidence[:3]

    def _aim_snap_evidence(self, events: list[MatchEvent]) -> list[Evidence]:
        evidence = []
        aim_events = [event for event in events if "view_angle" in event.payload]
        for previous, current in zip(aim_events, aim_events[1:]):
            elapsed = current.ts - previous.ts
            if elapsed <= 0 or elapsed > self.aim_snap_window:
                continue

            previous_angle = _angle(previous)
            current_angle = _angle(current)
            if previous_angle is None or current_angle is None:
                continue

            delta = _angular_delta(previous_angle, current_angle)
            if delta > self.aim_snap_degrees and current.payload.get("hit") is True:
                evidence.append(
                    Evidence(
                        reason="inhuman_aim_snap",
                        weight=30,
                        event_ts=current.ts,
                        detail=f"aim changed {delta:.1f} degrees in {elapsed:.2f}s before a hit",
                    )
                )
        return evidence[:3]

    def _combat_ratio_evidence(self, events: list[MatchEvent]) -> list[Evidence]:
        shot_events = [event for event in events if event.type == "shot"]
        if len(shot_events) < 8:
            return []

        hits = [event for event in shot_events if event.payload.get("hit") is True]
        headshots = [event for event in hits if event.payload.get("headshot") is True]
        hidden_hits = [event for event in hits if event.payload.get("target_visible") is False]

        evidence = []
        hit_rate = len(hits) / len(shot_events)
        if len(shot_events) >= 10 and hit_rate >= 0.85:
            evidence.append(
                Evidence(
                    reason="abnormal_hit_rate",
                    weight=25,
                    event_ts=None,
                    detail=f"{len(hits)}/{len(shot_events)} shots hit targets",
                )
            )

        if len(hits) >= 6:
            headshot_rate = len(headshots) / len(hits)
            if headshot_rate >= 0.75:
                evidence.append(
                    Evidence(
                        reason="abnormal_headshot_rate",
                        weight=20,
                        event_ts=None,
                        detail=f"{len(headshots)}/{len(hits)} hits were headshots",
                    )
                )

        if len(hidden_hits) >= 3:
            evidence.append(
                Evidence(
                    reason="repeated_hits_on_hidden_targets",
                    weight=30,
                    event_ts=hidden_hits[-1].ts,
                    detail=f"{len(hidden_hits)} hits occurred while target_visible=false",
                )
            )

        return evidence

    def _report_evidence(self, events: list[MatchEvent]) -> list[Evidence]:
        reports = [event for event in events if event.type == "report"]
        reporters = {
            str(event.payload.get("reporter_id"))
            for event in reports
            if event.payload.get("reporter_id")
        }
        if len(reporters) < 2:
            return []

        weight = min(20, len(reporters) * 5)
        return [
            Evidence(
                reason="multiple_player_reports",
                weight=weight,
                event_ts=reports[-1].ts,
                detail=f"{len(reporters)} unique players reported this player",
            )
        ]

    @staticmethod
    def _action_for_score(score: int) -> str:
        if score >= 80:
            return "urgent_manual_review"
        if score >= 50:
            return "manual_review"
        return "monitor"


def analyze_events(raw_events: Iterable[dict]) -> list[RiskReport]:
    events = [MatchEvent.from_dict(raw) for raw in raw_events]
    return RiskScorer().analyze(events)


def _position(event: MatchEvent) -> tuple[float, float, float] | None:
    raw = event.payload.get("position")
    if not isinstance(raw, dict):
        return None
    try:
        return float(raw["x"]), float(raw["y"]), float(raw["z"])
    except (KeyError, TypeError, ValueError):
        return None


def _angle(event: MatchEvent) -> tuple[float, float] | None:
    raw = event.payload.get("view_angle")
    if not isinstance(raw, dict):
        return None
    try:
        return float(raw["yaw"]), float(raw["pitch"])
    except (KeyError, TypeError, ValueError):
        return None


def _distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2 + (b[2] - a[2]) ** 2)


def _angular_delta(a: tuple[float, float], b: tuple[float, float]) -> float:
    yaw_delta = abs((b[0] - a[0] + 180) % 360 - 180)
    pitch_delta = abs(b[1] - a[1])
    return sqrt(yaw_delta**2 + pitch_delta**2)
