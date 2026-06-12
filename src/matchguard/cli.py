from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from matchguard.cases import build_moderation_cases
from matchguard.config import ScoringConfig
from matchguard.models import MatchEvent
from matchguard.models import RiskReport
from matchguard.scoring import RiskScorer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="matchguard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a JSONL match event file")
    analyze_parser.add_argument("path", type=Path, help="Path to newline-delimited JSON events")
    analyze_parser.add_argument("--config", type=Path, help="Path to a scoring config JSON file")
    analyze_parser.add_argument(
        "--min-score",
        type=int,
        default=1,
        help="Only print reports at or above this risk score",
    )

    cases_parser = subparsers.add_parser(
        "export-cases",
        help="Analyze a JSONL file and export moderation cases",
    )
    cases_parser.add_argument("path", type=Path, help="Path to newline-delimited JSON events")
    cases_parser.add_argument("--config", type=Path, help="Path to a scoring config JSON file")
    cases_parser.add_argument(
        "--min-score",
        type=int,
        default=1,
        help="Only export cases at or above this risk score",
    )

    args = parser.parse_args(argv)
    try:
        if args.command == "analyze":
            return _analyze(args.path, args.min_score, args.config)
        if args.command == "export-cases":
            return _export_cases(args.path, args.min_score, args.config)
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"matchguard: error: {exc}\n")
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


def _analyze(path: Path, min_score: int, config_path: Path | None) -> int:
    reports = _analyze_reports(path, config_path)
    filtered = _filter_reports(reports, min_score)
    json.dump({"reports": filtered}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def _export_cases(path: Path, min_score: int, config_path: Path | None) -> int:
    reports = _analyze_reports(path, config_path)
    filtered = [report for report in reports if report.risk_score >= min_score]
    cases = [case.to_dict() for case in build_moderation_cases(filtered)]
    json.dump({"cases": cases}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def _analyze_reports(path: Path, config_path: Path | None) -> list[RiskReport]:
    events = _load_events(path)
    config = ScoringConfig.from_path(config_path) if config_path else None
    return RiskScorer(config=config).analyze(events)


def _filter_reports(reports: list[RiskReport], min_score: int) -> list[dict[str, Any]]:
    return [report.to_dict() for report in reports if report.risk_score >= min_score]


def _load_events(path: Path) -> list[MatchEvent]:
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
            try:
                events.append(MatchEvent.from_dict(raw))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{path}:{line_number}: invalid event: {exc}") from exc
    return events


if __name__ == "__main__":
    raise SystemExit(main())
