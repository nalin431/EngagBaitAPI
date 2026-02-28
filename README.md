# Engagement Bait API

Analyze structural engagement-bait patterns in text. The API scores urgency pressure, low evidence signal, arousal intensity, counterargument absence, claim volume vs depth, and an optional OpenAI-powered semantic similarity signal.

This project is built for HackIllinois 2026 with a primary focus on API quality and developer experience.

## What It Does

- Detects structural manipulation patterns in text
- Returns transparent heuristic breakdowns for each metric
- Optionally adds `engagement_bait_score` using OpenAI embeddings
- Includes a lightweight browser demo for quick judging and testing
- Treats the `evidence_density` field as an inverted signal, where higher means less evidence

## What It Does Not Do

- Fact check claims
- Classify political ideology
- Detect truthfulness
- Perform content moderation

## Tech Stack

- FastAPI
- Python 3.10+
- Pydantic
- OpenAI embeddings via `text-embedding-3-small`

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Optional:

```bash
set OPENAI_API_KEY=your_key_here
```

Local URLs:

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Demo: `http://localhost:8000/demo`

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | API overview and key links |
| GET | `/health` | Health status and integration flags |
| GET | `/demo` | Lightweight browser demo |
| POST | `/analyze` | Analyze one text |
| POST | `/analyze/batch` | Analyze up to 10 texts |

## Analyze One Text

`POST /analyze`

Request body:

```json
{
  "text": "Your text to analyze..."
}
```

Query param:

- `ml=true|false`
- If omitted, ML defaults to on only when `OPENAI_API_KEY` is available

Constraints:

- text length: 50 to 50,000 characters

Example:

```bash
curl -X POST "http://localhost:8000/analyze?ml=true" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Act now. This is your last chance to see the truth before it disappears. Everyone knows they are lying, and if you do not share this immediately, more people will be fooled. There is no middle ground, and the answer is obvious.\"}"
```

Example response:

```json
{
  "urgency_pressure": {
    "score": 0.67,
    "breakdown": {
      "time_pressure": 1.0,
      "scarcity": 0.0,
      "fomo": 1.0
    }
  },
  "evidence_density": {
    "score": 1.0,
    "breakdown": {
      "citations": 1.0,
      "stats": 1.0,
      "external_sources": 1.0
    }
  },
  "arousal_intensity": {
    "score": 0.46,
    "breakdown": {
      "emotion_words": 0.33,
      "exclamation_density": 0.0,
      "question_density": 0.0,
      "caps_ratio": 0.0,
      "moralized_language": 0.25,
      "superlative_density": 0.0,
      "curiosity_gap": 0.0
    }
  },
  "counterargument_absence": {
    "score": 0.63,
    "breakdown": {
      "tradeoff_absence": 1.0,
      "conditional_absence": 0.25
    }
  },
  "claim_volume_vs_depth": {
    "score": 0.6,
    "breakdown": {
      "claims_per_word": 0.64,
      "explanation_depth": 0.19,
      "listicle": 0.0
    }
  },
  "engagement_bait_score": null,
  "meta": {
    "ml_requested": true,
    "ml_used": false,
    "openai_available": false,
    "vector_backend": "none"
  }
}
```

Note: `evidence_density` is an inverted bait signal. Higher values mean the text includes less evidence, not more.

`counterargument_absence` is also bait-oriented: higher values mean the text does less to acknowledge tradeoffs, conditions, or competing considerations.

## Analyze In Batch

`POST /analyze/batch`

Request body:

```json
{
  "items": [
    { "id": "high", "text": "First text..." },
    { "id": "neutral", "text": "Second text..." }
  ]
}
```

Rules:

- at least 1 item
- at most 10 items
- each item must satisfy the same text length validation as `/analyze`

The response preserves the order of the submitted items and includes each caller-supplied `id`.

## Response Meta

Each analysis response now includes:

```json
"meta": {
  "ml_requested": true,
  "ml_used": false,
  "openai_available": false,
  "vector_backend": "none"
}
```

Field meanings:

- `ml_requested`: whether the request asked for ML
- `ml_used`: whether the ML path actually ran
- `openai_available`: whether the server has a valid OpenAI key configured
- `vector_backend`: `none`, `centroid`, or `actian`

For the current submission, `vector_backend` will normally be:

- `none` when ML is off or unavailable
- `centroid` when OpenAI embeddings are used

## Browser Demo

The demo lives at `GET /demo`.

It includes:

- paste-in text analysis
- a `Use ML` toggle
- sample inputs for high bait, neutral, and mixed text
- score cards for all metrics
- raw JSON output for developer inspection

## Error Responses

Common validation errors:

- text too short
- text too long
- empty batch
- batch larger than 10 items

All validation errors return HTTP `422`.

## Testing

Run:

```bash
python -m pytest -q
```

## OpenAI Notes

The OpenAI portion of the project is intentionally narrow:

- embeddings power `engagement_bait_score`
- heuristic metrics remain the explainable layer
- if OpenAI is unavailable, the API still returns all heuristic results cleanly

## Project Status

This submission is optimized for:

- Stripe Track
- Best Use of OpenAI API

Actian Vector support remains future-facing and is not treated as a shipped dependency for the current submission.
