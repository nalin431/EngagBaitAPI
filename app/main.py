from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.models import AnalyzeRequest, AnalyzeResponse, MIN_TEXT_LEN, MAX_TEXT_LEN

app = FastAPI(
    title="Engagement Bait API",
    description="Detect structural manipulation in text: urgency pressure, evidence density, overconfidence, arousal, in-group/out-group markers, narrative simplification, claim volume vs depth.",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {
        "name": "Engagement Bait API",
        "docs": "/docs",
        "health": "/health",
        "analyze": "POST /analyze",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = errors[0]["msg"] if errors else "Validation error"
    loc = errors[0].get("loc", ())
    return JSONResponse(
        status_code=422,
        content={"detail": msg, "field": loc[-1] if loc else None},
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest, ml: bool | None = None):
    """Analyze text. Pass ?ml=true|false to enable/disable ML layer (default: true when OPENAI_API_KEY set)."""
    from app.analyzers import analyze_text
    return analyze_text(request.text, ml=ml)
