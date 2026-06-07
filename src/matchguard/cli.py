from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from matchguard.models import MatchEvent
from matchguard.scoring import RiskScorer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="matchguard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a JSONL match event file")
    analyze_parser.add_argument("path", type=Path, help="Path to newline-delimited JSON events")
    analyze_parser.add_argument(
        "--min-score",
        type=int,
        default=1,
        help="Only print reports at or above this risk score",
    )

    args = parser.parse_args(argv)
    if args.command == "analyze":
        return _analyze(args.path, args.min_score)

    parser.error(f"unknown command: {args.command}")
    return 2


def _analyze(path: Path, min_score: int) -> int:
    raw_events = _load_jsonl(path)
    events = [MatchEvent.from_dict(raw) for raw in raw_events]
    reports = RiskScorer().analyze(events)
    filtered = [report.to_dict() for report in reports if report.risk_score >= min_score]
    json.dump({"reports": filtered}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    events = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                raw = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(raw, dict):
                raise ValueError(f"{path}:{line_number}: event must be a JSON object")
            events.append(raw)
    return events


if __name__ == "__main__":
    raise SystemExit(main())
