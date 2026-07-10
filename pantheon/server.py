"""FastAPI server: serves the dashboard and streams live runs over SSE.

Run:  uvicorn pantheon.server:app --port 4173
Then open http://localhost:4173 , type a ticker, and watch the agents work.
"""

from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")  # API keys

app = FastAPI(title="Pantheon")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stream")
def stream(ticker: str, date: str = "2024-05-10", provider: str | None = None,
           deep: str | None = None, quick: str | None = None):
    """Server-Sent Events: one message per agent as the pipeline runs (live data)."""
    from pantheon.config import get_config, reset_config, set_config
    from pantheon.graph.run import stream_pipeline

    reset_config()
    overrides: dict = {}
    if provider:
        overrides["llm_provider"] = provider
    if deep:
        overrides["deep_think_llm"] = deep
    if quick:
        overrides["quick_think_llm"] = quick
    if overrides:
        set_config(overrides)
    cfg = get_config()

    def gen():
        # announce the run
        yield _sse({"agent": "System", "team": "scanner",
                    "role": f"{cfg['llm_provider']} · live data",
                    "content": f"Analyzing **{ticker.upper()}** as of {date}…"})
        try:
            for event in stream_pipeline(ticker.upper(), date, config=cfg):
                yield _sse(event)
        except Exception as exc:  # noqa: BLE001 — surface errors to the UI
            yield _sse({"error": str(exc)})

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj)}\n\n"


# Serve the dashboard (mounted last so /api/* wins).
_FRONTEND = _ROOT / "frontend"
if _FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND), html=True), name="frontend")
