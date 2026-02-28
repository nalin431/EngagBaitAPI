from pydantic import BaseModel, Field, field_validator

MIN_TEXT_LEN = 50
MAX_TEXT_LEN = 50_000


class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        description=f"Text to analyze ({MIN_TEXT_LEN}-{MAX_TEXT_LEN} characters)",
        json_schema_extra={"minLength": MIN_TEXT_LEN, "maxLength": MAX_TEXT_LEN},
    )

    @field_validator("text")
    @classmethod
    def validate_text_length(cls, v: str) -> str:
        if len(v) < MIN_TEXT_LEN:
            raise ValueError(
                f"Text must be at least {MIN_TEXT_LEN} characters (got {len(v)})"
            )
        if len(v) > MAX_TEXT_LEN:
            raise ValueError(
                f"Text must be at most {MAX_TEXT_LEN} characters (got {len(v)})"
            )
        return v


class MetricBreakdown(BaseModel):
    score: float = Field(..., ge=0, le=1)
    breakdown: dict[str, float] = Field(default_factory=dict)


class AnalyzeResponse(BaseModel):
    urgency_pressure: MetricBreakdown
    evidence_density: MetricBreakdown
    arousal_intensity: MetricBreakdown
    narrative_simplification: MetricBreakdown
    claim_volume_vs_depth: MetricBreakdown
    engagement_bait_score: float | None = Field(
        default=None,
        description="ML-based engagement bait score (0–1); null when OpenAI unavailable",
    )
