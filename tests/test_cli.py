import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import path_setup  # noqa: F401
from matchguard.cli import main


class CliTests(unittest.TestCase):
    def test_analyze_prints_json_reports(self):
        events_path = self._write_jsonl(
            [
                {
                    "match_id": "m1",
                    "player_id": "p1",
                    "type": "movement",
                    "ts": 1.0,
                    "position": {"x": 0, "y": 0, "z": 0},
                },
                {
                    "match_id": "m1",
                    "player_id": "p1",
                    "type": "movement",
                    "ts": 1.1,
                    "position": {"x": 100, "y": 0, "z": 0},
                },
            ]
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["analyze", str(events_path)])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["reports"][0]["player_id"], "p1")
        self.assertEqual(payload["reports"][0]["risk_score"], 25)

    def test_export_cases_prints_review_cases(self):
        events_path = self._write_jsonl(
            [
                {
                    "match_id": "m1",
                    "player_id": "p1",
                    "type": "movement",
                    "ts": 1.0,
                    "position": {"x": 0, "y": 0, "z": 0},
                },
                {
                    "match_id": "m1",
                    "player_id": "p1",
                    "type": "movement",
                    "ts": 1.1,
                    "position": {"x": 100, "y": 0, "z": 0},
                },
            ]
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["export-cases", str(events_path)])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["cases"][0]["severity"], "low")
        self.assertTrue(payload["cases"][0]["case_id"].startswith("case_"))

    def test_invalid_event_returns_clean_error(self):
        events_path = self._write_text('{"match_id": "m1", "player_id": "p1"}\n')

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = main(["analyze", str(events_path)])

        self.assertEqual(exit_code, 1)
        self.assertIn("invalid event", stderr.getvalue())
        self.assertIn("missing required fields", stderr.getvalue())

    def _write_jsonl(self, events: list[dict]) -> Path:
        return self._write_text("".join(f"{json.dumps(event)}\n" for event in events))

    def _write_text(self, content: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "events.jsonl"
        path.write_text(content, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
