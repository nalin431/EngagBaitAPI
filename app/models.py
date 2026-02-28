from pydantic import BaseModel, Field

MIN_TEXT_LEN = 50
MAX_TEXT_LEN = 50_000


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=MIN_TEXT_LEN, max_length=MAX_TEXT_LEN)


class MetricBreakdown(BaseModel):
    score: float = Field(..., ge=0, le=1)
    breakdown: dict[str, float] = Field(default_factory=dict)


class AnalyzeResponse(BaseModel):
    urgency_pressure: MetricBreakdown
    evidence_density: MetricBreakdown
    overconfidence: MetricBreakdown
    arousal_intensity: MetricBreakdown
    ingroup_outgroup: MetricBreakdown
    narrative_simplification: MetricBreakdown
    claim_volume_vs_depth: MetricBreakdown
