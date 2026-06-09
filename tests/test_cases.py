import unittest

from matchguard.cases import build_moderation_case
from matchguard.models import Evidence, RiskReport


class ModerationCaseTests(unittest.TestCase):
    def test_builds_stable_moderation_case(self):
        report = RiskReport(
            match_id="match-001",
            player_id="player-17",
            risk_score=85,
            reasons=["inhuman_aim_snap", "abnormal_hit_rate"],
            evidence=[
                Evidence(
                    reason="abnormal_hit_rate",
                    weight=25,
                    event_ts=None,
                    detail="9/10 shots hit targets",
                ),
                Evidence(
                    reason="inhuman_aim_snap",
                    weight=30,
                    event_ts=12.5,
                    detail="aim changed 85 degrees in 0.10s before a hit",
                ),
            ],
            action="urgent_manual_review",
        )

        case = build_moderation_case(report)

        self.assertTrue(case.case_id.startswith("case_"))
        self.assertEqual(case.severity, "critical")
        self.assertEqual(case.recommended_action, "urgent_manual_review")
        self.assertEqual(case.timeline[0]["event_ts"], 12.5)
        self.assertIn("player-17 scored 85/100", case.summary)


if __name__ == "__main__":
    unittest.main()
