import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    BatchAnalyzeResult,
)

load_dotenv()

_DESCRIPTION = """
Six interpretable metrics. One POST request. No black box.

Analyze structural engagement-bait patterns in any text — articles, emails, tweets, social posts —
with a lightweight, fully deterministic heuristic layer and an optional OpenAI embedding-based
semantic score. Every response includes a transparent breakdown showing exactly which signals fired
and how much they contributed.

**Live demo:** [engagbaitapi.onrender.com/demo](https://engagbaitapi.onrender.com/demo)

---

## Metrics

| Metric | What it measures |
|---|---|
| `urgency_pressure` | Time pressure, scarcity, and FOMO signals |
| `evidence_density` | Absence of citations, statistics, and sourcing *(inverted)* |
| `arousal_intensity` | Emotional heat: emotion vocabulary, moralized language, caps, curiosity gaps |
| `counterargument_absence` | Absence of hedging, tradeoffs, or competing views *(inverted)* |
| `claim_volume_vs_depth` | Many assertions, little explanation |
| `lexical_diversity` | Repetitive / sloganeering vocabulary via MATTR *(inverted)* |
| `engagement_bait_score` | Optional OpenAI embeddings score (0–1), `null` when unavailable |

---

## Design principles

- **Fully deterministic** — heuristic scores have no randomness or model state; same input always returns the same output
- **Privacy-safe** — text is analyzed in-memory and discarded; heuristic mode makes zero external API calls
- **Transparent** — every score includes a `breakdown` dict showing sub-signal contributions
- **Fits any stack** — plain JSON over HTTP, no SDK required

---

## Error format

All validation errors return `HTTP 422`:

```json
{"detail": "Text must be at least 50 characters (got 12)", "field": "text"}
```
"""

_TAGS = [
    {
        "name": "Analysis",
        "description": "Score text for engagement-bait signals. Supports single and batch requests.",
    },
    {
        "name": "System",
        "description": "Health, metadata, and the browser demo.",
    },
]

app = FastAPI(
    title="Engagement Bait API",
    description=_DESCRIPTION,
    version="0.1.0",
    openapi_tags=_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _openai_enabled() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip().startswith("sk-"))


@app.get(
    "/",
    tags=["System"],
    summary="API overview",
    description="Return core API links and metadata. Useful as a discovery endpoint.",
)
async def root():
    return {
        "name": "Engagement Bait API",
        "version": app.version,
        "description": "Analyze structural engagement-bait patterns in text.",
        "docs": "/docs",
        "demo": "/demo",
        "health": "/health",
        "analyze": "/analyze",
        "analyze_batch": "/analyze/batch",
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description=(
        "Return service status and whether the OpenAI embeddings path is available. "
        "`openai_enabled: true` means a valid API key is configured and embeddings scoring will run."
    ),
)
async def health():
    return {
        "status": "ok",
        "openai_enabled": _openai_enabled(),
    }


@app.get(
    "/demo",
    tags=["System"],
    summary="Browser demo",
    description=(
        "Serve the interactive browser demo. Paste any text, toggle embeddings on or off, "
        "and see all six metric score cards plus raw JSON output. "
        "Three sample inputs are included: high bait, neutral, and mixed."
    ),
)
async def demo():
    return FileResponse(STATIC_DIR / "index.html")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = errors[0]["msg"] if errors else "Validation error"
    loc = errors[0].get("loc", ())
    return JSONResponse(
        status_code=422,
        content={"detail": msg, "field": loc[-1] if loc else None},
    )


@app.post(
    "/analyze",
    tags=["Analysis"],
    response_model=AnalyzeResponse,
    summary="Analyze one text",
    description="""Score one text for structural engagement-bait patterns.

Returns six metrics, each with a `score` (0–1) and a `breakdown` dict of sub-signals.
Also returns a `meta` object describing whether the embeddings path ran.

**Query parameter:** `embeddings=true|false`
- `true` — always attempt embeddings scoring (requires OpenAI key on server)
- `false` — heuristics only, no external calls
- omitted — embeddings run automatically if an OpenAI key is configured

**Text constraints:** 50–50,000 characters

**Example (curl):**
```bash
curl -s -X POST "https://engagbaitapi.onrender.com/analyze?embeddings=false" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Act now. This is your last chance. Everyone knows they are lying and you must share this immediately."}'
```
""",
)
async def analyze(request: AnalyzeRequest, embeddings: bool | None = None):
    from app.analyzers import analyze_text

    return analyze_text(request.text, ml=embeddings)


@app.post(
    "/analyze/batch",
    tags=["Analysis"],
    response_model=BatchAnalyzeResponse,
    summary="Analyze multiple texts",
    description="""Analyze up to 10 texts in a single request.

Response preserves submission order and echoes each caller-supplied `id`.
Accepts the same `embeddings` query parameter as `/analyze` — applies uniformly to all items.

**Batch constraints:**
- 1–10 items per request
- Each item text: 50–50,000 characters

**Example (curl):**
```bash
curl -s -X POST "https://engagbaitapi.onrender.com/analyze/batch?embeddings=false" \\
  -H "Content-Type: application/json" \\
  -d '{
    "items": [
      {"id": "bait", "text": "Act now. This is your last chance. Everyone knows they are lying and you must share this immediately."},
      {"id": "neutral", "text": "A review of three transit funding proposals found ridership increased 12 to 18 percent in pilot cities, though the report notes significant regional cost variation and recommends further study."}
    ]
  }'
```
""",
)
async def analyze_batch(request: BatchAnalyzeRequest, embeddings: bool | None = None):
    from app.analyzers import analyze_text

    return BatchAnalyzeResponse(
        items=[
            BatchAnalyzeResult(id=item.id, result=analyze_text(item.text, ml=embeddings))
            for item in request.items
        ]
    )
