from typing import Literal

from pydantic import BaseModel, Field, field_validator

MIN_TEXT_LEN = 50
MAX_TEXT_LEN = 50_000


def validate_text_length_value(v: str) -> str:
    if len(v) < MIN_TEXT_LEN:
        raise ValueError(
            f"Text must be at least {MIN_TEXT_LEN} characters (got {len(v)})"
        )
    if len(v) > MAX_TEXT_LEN:
        raise ValueError(
            f"Text must be at most {MAX_TEXT_LEN} characters (got {len(v)})"
        )
    return v


class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        description=f"Text to analyze ({MIN_TEXT_LEN}-{MAX_TEXT_LEN} characters)",
        json_schema_extra={"minLength": MIN_TEXT_LEN, "maxLength": MAX_TEXT_LEN},
    )

    @field_validator("text")
    @classmethod
    def validate_text_length(cls, v: str) -> str:
        return validate_text_length_value(v)


class MetricBreakdown(BaseModel):
    score: float = Field(..., ge=0, le=1)
    breakdown: dict[str, float] = Field(default_factory=dict)


class AnalyzeMeta(BaseModel):
    ml_requested: bool
    ml_used: bool
    openai_available: bool
    vector_backend: Literal["none", "centroid", "actian"]


class AnalyzeResponse(BaseModel):
    urgency_pressure: MetricBreakdown
    evidence_density: MetricBreakdown
    arousal_intensity: MetricBreakdown
    counterargument_absence: MetricBreakdown
    claim_volume_vs_depth: MetricBreakdown
    engagement_bait_score: float | None = Field(
        default=None,
        description="ML-based engagement bait score (0-1); null when OpenAI unavailable",
    )
    meta: AnalyzeMeta


class BatchAnalyzeItem(BaseModel):
    id: str = Field(..., min_length=1)
    text: str = Field(
        ...,
        description=f"Text to analyze ({MIN_TEXT_LEN}-{MAX_TEXT_LEN} characters)",
        json_schema_extra={"minLength": MIN_TEXT_LEN, "maxLength": MAX_TEXT_LEN},
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        return validate_text_length_value(v)


class BatchAnalyzeRequest(BaseModel):
    items: list[BatchAnalyzeItem]

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list[BatchAnalyzeItem]) -> list[BatchAnalyzeItem]:
        if not v:
            raise ValueError("Batch must include at least 1 item")
        if len(v) > 10:
            raise ValueError("Batch must include at most 10 items")
        return v


class BatchAnalyzeResult(BaseModel):
    id: str
    result: AnalyzeResponse


class BatchAnalyzeResponse(BaseModel):
    items: list[BatchAnalyzeResult]
