# MatchGuard

Open-source anti-cheat telemetry and moderation toolkit for indie multiplayer games.

MatchGuard helps game developers collect server-side match events, calculate player risk scores, and create review-ready moderation cases. It is designed for small teams that need practical anti-cheat signals without shipping invasive client-side software or relying on automatic bans.

## Why this exists

Most small multiplayer games do not have the budget for a full anti-cheat team. At the same time, player reports, suspicious match replays, and raw server logs are hard to review manually.

MatchGuard focuses on explainable signals:

- abnormal movement speed;
- suspicious aim snaps;
- high hit or headshot rates;
- hits against non-visible targets;
- repeated reports from other players;
- review cases with reasons and evidence.

The goal is not to ban players automatically. The goal is to help moderators find the cases that deserve attention.

## Current status

This repository is an early MVP. It includes:

- a Python scoring engine;
- a JSONL command-line analyzer;
- an optional FastAPI server adapter;
- an example Unity client script;
- a sample match event dataset;
- docs for architecture, privacy, roadmap, and OSS application positioning.

## Quick start

Analyze the included sample events:

```powershell
$env:PYTHONPATH = "src"
python -m matchguard.cli analyze examples/events/sample_match.jsonl
```

Run with a stricter scoring profile:

```powershell
python -m matchguard.cli analyze examples/events/sample_match.jsonl --config examples/config/strict.json
```

Or install in editable mode:

```powershell
python -m pip install -e .
matchguard analyze examples/events/sample_match.jsonl
```

## Event format

Events are newline-delimited JSON objects:

```json
{
  "match_id": "match-001",
  "player_id": "player-17",
  "type": "shot",
  "ts": 12.42,
  "view_angle": { "yaw": 91.0, "pitch": 4.0 },
  "hit": true,
  "headshot": true,
  "target_visible": false
}
```

See [schemas/match_event.schema.json](schemas/match_event.schema.json) and [examples/events/sample_match.jsonl](examples/events/sample_match.jsonl).

## API concept

The optional API accepts a batch of events and returns risk reports:

```http
POST /analyze
Content-Type: application/json
```

```json
{
  "events": [
    {
      "match_id": "match-001",
      "player_id": "player-17",
      "type": "movement",
      "ts": 1.0,
      "position": { "x": 0, "y": 0, "z": 0 }
    }
  ]
}
```

## Project principles

- Explainable signals over black-box bans.
- Server-side telemetry first.
- Human review by default.
- Privacy-aware event collection.
- Engine-friendly SDKs and examples.

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).

## OpenAI Codex for OSS

This project is structured to be a useful OSS candidate: it has a clear maintainer workflow, tests, examples, documentation, and a realistic path for AI-assisted maintenance.

See [docs/codex-for-oss-application.md](docs/codex-for-oss-application.md) for draft application text.

## License

MIT License. See [LICENSE](LICENSE).
