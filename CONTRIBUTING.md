# Contributing

Thanks for helping improve MatchGuard.

Good first contributions:

- add sample events for different game genres;
- improve scoring explanations;
- add tests for edge cases;
- improve Unity integration examples;
- document server-authoritative event patterns.

Please keep the project focused on explainable moderation assistance. Features that encourage automatic bans or invasive player surveillance need strong justification and privacy review.

Before opening a change, run:

```powershell
python -m unittest
```

For lint checks, install the development extra and run Ruff:

```powershell
python -m pip install -e ".[dev]"
python -m ruff check .
```
