"""MatchGuard scoring engine."""

from matchguard.cases import ModerationCase, build_moderation_case, build_moderation_cases
from matchguard.config import ScoringConfig
from matchguard.models import Evidence, MatchEvent, RiskReport
from matchguard.scoring import RiskScorer, analyze_events

__all__ = [
    "Evidence",
    "MatchEvent",
    "ModerationCase",
    "RiskReport",
    "ScoringConfig",
    "RiskScorer",
    "analyze_events",
    "build_moderation_case",
    "build_moderation_cases",
]
