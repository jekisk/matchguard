# CLI Usage

MatchGuard includes a small command-line analyzer for local datasets and CI checks.

## Analyze a JSONL file

```powershell
$env:PYTHONPATH = "src"
python -m matchguard.cli analyze examples/events/sample_match.jsonl
```

## Use a scoring profile

```powershell
python -m matchguard.cli analyze examples/events/sample_match.jsonl --config examples/config/strict.json
```

## Filter low-risk reports

```powershell
python -m matchguard.cli analyze examples/events/sample_match.jsonl --min-score 50
```

The CLI prints JSON so it can be saved by CI jobs, attached to moderation reports, or forwarded into a dashboard prototype.
