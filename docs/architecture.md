# Architecture

MatchGuard is split into four small pieces.

## Game integration

The game client or server emits match events:

- movement snapshots;
- shot attempts;
- hit confirmation;
- target visibility;
- player reports;
- moderation outcomes.

For competitive games, server-authoritative events should be preferred over client-only events.

## Event ingestion

Events can be sent as JSON batches to an HTTP API or exported as JSONL for offline review. The MVP keeps ingestion simple so teams can adapt it to existing game backends.

## Risk scoring

The first scorer is rule-based and explainable. Each signal adds weighted evidence to a player report. The output includes:

- score;
- reasons;
- evidence details;
- recommended action.

## Moderator review

MatchGuard should create a queue for humans, not automatic punishments. Future versions can include a web dashboard, replay timestamps, Discord webhooks, and confirmed/false-positive feedback loops.
