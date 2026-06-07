from __future__ import annotations

from typing import Any

from matchguard.scoring import analyze_events


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
    except ImportError as exc:
        raise RuntimeError("Install the API extras with: pip install 'matchguard[api]'") from exc

    class AnalyzeRequest(BaseModel):
        events: list[dict[str, Any]]

    app = FastAPI(
        title="MatchGuard API",
        version="0.1.0",
        description="Analyze multiplayer match telemetry and return moderation risk reports.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/analyze")
    def analyze(request: AnalyzeRequest) -> dict[str, Any]:
        reports = analyze_events(request.events)
        return {"reports": [report.to_dict() for report in reports]}

    return app


app = create_app()
