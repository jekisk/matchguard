import unittest

from matchguard.config import ScoringConfig
from matchguard.models import MatchEvent
from matchguard.scoring import RiskScorer, analyze_events


class ScoringTests(unittest.TestCase):
    def test_reports_hidden_target_and_high_hit_rate(self):
        raw_events = []
        for index in range(10):
            raw_events.append(
                {
                    "match_id": "m1",
                    "player_id": "p1",
                    "type": "shot",
                    "ts": float(index),
                    "view_angle": {"yaw": 10 + index, "pitch": 2},
                    "hit": index < 9,
                    "headshot": index < 7,
                    "target_visible": index > 4,
                }
            )

        reports = analyze_events(raw_events)

        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].player_id, "p1")
        self.assertIn("abnormal_hit_rate", reports[0].reasons)
        self.assertIn("repeated_hits_on_hidden_targets", reports[0].reasons)

    def test_abnormal_movement_speed_is_reported(self):
        events = [
            MatchEvent.from_dict(
                {
                    "match_id": "m1",
                    "player_id": "p1",
                    "type": "movement",
                    "ts": 1.0,
                    "position": {"x": 0, "y": 0, "z": 0},
                }
            ),
            MatchEvent.from_dict(
                {
                    "match_id": "m1",
                    "player_id": "p1",
                    "type": "movement",
                    "ts": 1.1,
                    "position": {"x": 100, "y": 0, "z": 0},
                }
            ),
        ]

        reports = RiskScorer().analyze(events)

        self.assertEqual(reports[0].reasons, ["abnormal_movement_speed"])
        self.assertEqual(reports[0].risk_score, 25)

    def test_clean_player_does_not_get_report(self):
        raw_events = [
            {
                "match_id": "m1",
                "player_id": "p2",
                "type": "movement",
                "ts": 1.0,
                "position": {"x": 0, "y": 0, "z": 0},
            },
            {
                "match_id": "m1",
                "player_id": "p2",
                "type": "movement",
                "ts": 2.0,
                "position": {"x": 4, "y": 0, "z": 0},
            },
        ]

        self.assertEqual(analyze_events(raw_events), [])

    def test_custom_config_can_tune_speed_threshold(self):
        events = [
            MatchEvent.from_dict(
                {
                    "match_id": "m1",
                    "player_id": "p1",
                    "type": "movement",
                    "ts": 1.0,
                    "position": {"x": 0, "y": 0, "z": 0},
                }
            ),
            MatchEvent.from_dict(
                {
                    "match_id": "m1",
                    "player_id": "p1",
                    "type": "movement",
                    "ts": 2.0,
                    "position": {"x": 12, "y": 0, "z": 0},
                }
            ),
        ]

        default_reports = RiskScorer().analyze(events)
        strict_reports = RiskScorer(
            config=ScoringConfig(max_speed_units_per_second=10.0)
        ).analyze(events)

        self.assertEqual(default_reports, [])
        self.assertEqual(strict_reports[0].reasons, ["abnormal_movement_speed"])


if __name__ == "__main__":
    unittest.main()
