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

app = FastAPI(
    title="Engagement Bait API",
    description=(
        "Analyze structural engagement-bait patterns in text with transparent "
        "heuristics and an optional semantic similarity score."
    ),
    version="0.1.0",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _openai_enabled() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip().startswith("sk-"))


@app.get("/", summary="API overview", description="Return the core API links and metadata.")
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
    summary="Health check",
    description="Return service status and optional integration availability.",
)
async def health():
    return {
        "status": "ok",
        "openai_enabled": _openai_enabled(),
    }


@app.get("/demo", summary="Browser demo", description="Serve the lightweight API demo page.")
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
    response_model=AnalyzeResponse,
    summary="Analyze one text",
    description=(
        "Score one text for structural engagement-bait patterns. "
        "Use the embeddings query parameter to opt into or out of semantic scoring."
    ),
)
async def analyze(request: AnalyzeRequest, embeddings: bool | None = None):
    from app.analyzers import analyze_text

    return analyze_text(request.text, ml=embeddings)


@app.post(
    "/analyze/batch",
    response_model=BatchAnalyzeResponse,
    summary="Analyze multiple texts",
    description="Analyze up to 10 texts in one request and preserve the submitted order.",
)
async def analyze_batch(request: BatchAnalyzeRequest, embeddings: bool | None = None):
    from app.analyzers import analyze_text

    return BatchAnalyzeResponse(
        items=[
            BatchAnalyzeResult(id=item.id, result=analyze_text(item.text, ml=embeddings))
            for item in request.items
        ]
    )
