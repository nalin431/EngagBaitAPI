# Engagement Bait API

Detect structural manipulation in text: urgency pressure, evidence density, arousal intensity, narrative simplification, and claim volume vs depth. Built for HackIllinois 2026 (Stripe Track).

## Tech Stack

- **FastAPI** – HTTP API, auto OpenAPI docs
- **Python 3.10+**
- **Pydantic** – request/response validation
- **OpenAI** – embeddings for ML layer (`engagement_bait_score`)
- **Actian VectorAI DB** – vector search (Phase 2b; SDK coming soon)

## Quick Start

```bash
# Create venv (optional)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS

# Install
pip install -r requirements.txt

# Optional: set OPENAI_API_KEY for ML layer (engagement_bait_score)
# cp .env.example .env && edit .env

# Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API overview + link to docs |
| GET | `/health` | Liveness check |
| POST | `/analyze` | Analyze text for engagement bait metrics |

## Analyze Request

**POST /analyze**

- **Content-Type:** `application/json`
- **Body:** `{ "text": "Your text to analyze..." }`
- **Constraints:** `text` length 50–50,000 characters
- **Query param:** `?ml=true|false` – enable/disable ML layer (default: true when `OPENAI_API_KEY` set)

## Example: cURL

```bash
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d "{\"text\": \"You must act now! This is the last chance. Everyone knows they are evil and we must fight back. The truth is simple: they are always wrong and we will never give up. Don't miss out!\"}"
```

## Example: Postman

1. New Request → POST
2. URL: `http://localhost:8000/analyze`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):

```json
{
  "text": "You must act now! This is the last chance. Everyone knows they are evil and we must fight back. The truth is simple: they are always wrong and we will never give up. Don't miss out!"
}
```

## Response Schema

All scores are 0–1; higher = more engagement-bait-like.

```json
{
  "urgency_pressure": { "score": 0.72, "breakdown": { "time_pressure": 0.8, "scarcity": 0.6, "fomo": 0.75 } },
  "evidence_density": { "score": 0.15, "breakdown": { "citations": 0, "stats": 0.2, "external_sources": 0.1 } },
  "arousal_intensity": { "score": 0.7, "breakdown": { "emotion_words": 0.75, "exclamation_density": 0.6, "question_density": 0.2, "caps_ratio": 0.1, "moralized_language": 0.8, "superlative_density": 0.5, "curiosity_gap": 0.3 } },
  "narrative_simplification": { "score": 0.8, "breakdown": { "binary_connectors": 0.85, "single_cause": 0.9, "tradeoff_absence": 0.7, "conditional_absence": 0.75 } },
  "claim_volume_vs_depth": { "score": 0.6, "breakdown": { "claims_per_word": 0.65, "explanation_depth": 0.55, "listicle": 0.2 } },
  "engagement_bait_score": 0.78
}
```

`engagement_bait_score` (0–1) is an ML-based score from OpenAI embeddings; it is `null` when `OPENAI_API_KEY` is not set.

## Metrics

| Metric | Sub-metrics | Description |
|--------|-------------|-------------|
| **Urgency Pressure** | time_pressure, scarcity, fomo | Time pressure, scarcity, FOMO phrases |
| **Evidence Density** | citations, stats, external_sources | Inverted: low evidence → high score |
| **Arousal Intensity** | emotion_words, exclamation_density, question_density, caps_ratio, moralized_language, superlative_density, curiosity_gap | High-arousal emotions, exclamations, questions, caps, moralized terms, superlatives, curiosity-gap phrases |
| **Narrative Simplification** | binary_connectors, single_cause, tradeoff_absence, conditional_absence | Either/or, single cause, no trade-offs |
| **Claim Volume vs Depth** | claims_per_word, explanation_depth, listicle | Many strong claims, shallow explanation, listicle patterns |
| **Engagement Bait (ML)** | — | Semantic similarity to bait vs neutral examples (OpenAI embeddings) |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Required for `engagement_bait_score` (embeddings) |
| `USE_ACTIAN` | Optional; if true, use Actian VectorAI DB for k-NN when available |
| `ACTIAN_*` | Actian VectorAI DB connection (per Actian docs; SDK coming soon) |

## Actian VectorAI DB (Phase 2b)

When Actian VectorAI DB SDK is released: set `USE_ACTIAN=true` and `ACTIAN_*` vars, then run:

```bash
python -m scripts.seed_actian
```

Until then, the ML layer uses in-memory centroid scoring (Phase 2a).

## Prize Eligibility

- **Best Use of OpenAI API** – OpenAI embeddings for semantic similarity
- **Best Use of Actian VectorAI DB** – Vector search integration (when SDK available)

## Error Responses

- **422 Unprocessable Entity** – Invalid input (e.g., text too short/long)
- **500 Internal Server Error** – Server error

## License

MIT
