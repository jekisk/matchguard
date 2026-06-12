# CLI Usage

MatchGuard includes a small command-line analyzer for local datasets and CI checks.

## Analyze a JSONL file

```powershell
$env:PYTHONPATH = "src"
python -m matchguard.cli analyze examples/events/sample_match.jsonl
```

After editable installation, you can use the console script:

```powershell
matchguard analyze examples/events/sample_match.jsonl
```

## Use a scoring profile

```powershell
python -m matchguard.cli analyze examples/events/sample_match.jsonl --config examples/config/strict.json
```

## Filter low-risk reports

```powershell
python -m matchguard.cli analyze examples/events/sample_match.jsonl --min-score 50
```

## Export moderation cases

```powershell
python -m matchguard.cli export-cases examples/events/sample_match.jsonl --min-score 50
```

Cases include stable IDs, severity, summaries, recommended actions, and evidence timelines.

## Summarize a dataset

```powershell
python -m matchguard.cli summarize examples/events/sample_match.jsonl --min-score 50
```

The summary output includes event count, match count, player count, flagged player count, action counts, top reasons, and the highest-risk players. It is designed for CI jobs, nightly telemetry checks, and quick moderator handoffs.

The CLI prints JSON so it can be saved by CI jobs, attached to moderation reports, or forwarded into a dashboard prototype.

Invalid JSONL rows, missing required event fields, missing files, and invalid scoring config files return a non-zero exit code with a concise `matchguard: error:` message on stderr.
