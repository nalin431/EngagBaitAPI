# Engagement Bait API

Analyze structural engagement-bait patterns in text. The API combines deterministic heuristic signals with an optional OpenAI embedding-based semantic similarity score.

This project is currently optimized around:
- a FastAPI backend
- an explainable deterministic layer
- an OpenAI-powered centroid embeddings score
- a lightweight browser demo
- an internal embeddings benchmark workflow

## What It Does

- Detects structural manipulation patterns in text
- Returns transparent heuristic breakdowns for each metric
- Optionally adds `engagement_bait_score` using OpenAI embeddings
- Includes a lightweight browser demo for quick judging and testing
- Provides an internal benchmark script for reviewing embeddings behavior on curated examples

## What It Does Not Do

- Fact check claims
- Classify political ideology
- Detect truthfulness
- Perform content moderation

Note that the deterministic layer does not attempt to produce a comprehensive "engagement bait score" and instead returns 5 potential components of engagement bait.

These signals do not exhaustively capture all forms of engagement engineering or narrative distortion, and therefore are not combined to create a final score.

This layer is intentionally interpretable, serving as a signal extractor instead of an all encompassing score.

## Tech Stack

- FastAPI
- Python 3.10+
- Pydantic
- OpenAI embeddings via `text-embedding-3-small`
- `python-dotenv` for local environment loading

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

Local configuration:

1. Copy `.env.example` to `.env`
2. Add your `OPENAI_API_KEY`

Local URLs:

- API: `http://localhost:5000`
- Docs: `http://localhost:5000/docs`
- Demo: `http://localhost:5000/demo`

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | API overview and key links |
| GET | `/health` | Health status and OpenAI availability |
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

- `embeddings=true|false`
- If omitted, embeddings defaults to on only when `OPENAI_API_KEY` is available

Constraints:

- text length: 50 to 50,000 characters

Example (Powershell):

```powershell

Invoke-RestMethod -Method Post -Uri "http://localhost:5000/analyze?embeddings=false" -ContentType "application/json" -Body (@{ text = "Act now. This is your last chance to see the truth before it disappears. Everyone knows they are lying, and if you do not share this immediately, more people will be fooled. There is no middle ground, and the answer is obvious." } | ConvertTo-Json -Compress)


```

Example response:

```json
{
  "urgency_pressure": {
    "score": 0.69,
    "breakdown": {
      "time_pressure": 1.0,
      "scarcity": 0.0,
      "fomo": 0.67
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
    "score": 0.35,
    "breakdown": {
      "emotion_words": 0.67,
      "exclamation_density": 0.0,
      "question_density": 0.0,
      "caps_ratio": 0.0,
      "moralized_language": 0.75,
      "superlative_density": 0.0,
      "curiosity_gap": 1.0
    }
  },
  "counterargument_absence": {
    "score": 1.0,
    "breakdown": {
      "tradeoff_absence": 1.0,
      "conditional_absence": 1.0
    }
  },
  "claim_volume_vs_depth": {
    "score": 0.62,
    "breakdown": {
      "claims_per_word": 1.0,
      "explanation_depth": 0.13,
      "listicle": 0.0
    }
  },
  "engagement_bait_score": null,
  "meta": {
    "embeddings_requested": false,
    "embeddings_used": false,
    "openai_available": false,
    "vector_backend": "none"
  }
}
```

Notes:

- `evidence_density` is an inverted bait signal. Higher values mean the text includes less evidence, not more.
- `counterargument_absence` is also bait-oriented. Higher values mean the text does less to acknowledge tradeoffs, conditions, or competing considerations.

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

Example meta when ML is requested but OpenAI is unavailable:

```json
"meta": {
  "embeddings_requested": true,
  "embeddings_used": false,
  "openai_available": false,
  "vector_backend": "none"
}
```

Field meanings:

- `embeddings_requested`: whether the request asked for embeddings scoring
- `embeddings_used`: whether the embeddings path actually ran
- `openai_available`: whether the server has a valid OpenAI key configured
- `vector_backend`: `none` or `centroid`

For the current project:

- `none` means the heuristic layer ran without embeddings
- `centroid` means OpenAI embeddings were used and scored against the bait/neutral seed centroids

## Browser Demo

The demo lives at `GET /demo`.

It includes:

- paste-in text analysis
- a `Use Embeddings` toggle
- sample inputs for high bait, neutral, and mixed text
- score cards for all metrics
- raw JSON output for developer inspection

## Embeddings Benchmark

The project includes an internal benchmark runner for reviewing OpenAI-backed embeddings behavior.

Run:

```bash
python -m scripts.run_ml_benchmark
```

Requirements:

- a valid `OPENAI_API_KEY`
- benchmark examples in `data/ml_benchmark_examples.json`

The script prints:

- benchmark id and label
- Embeddings score
- heuristic scores
- response metadata
- expected qualitative behavior
- notes for manual review

This is a manual evaluation tool, not a normal CI test.

## Testing

Run the automated tests with:

```bash
python -m pytest -q
```

## OpenAI Notes

The OpenAI portion of the project is intentionally narrow:

- embeddings power `engagement_bait_score`
- the scorer currently uses centroid similarity over curated bait and neutral seed examples
- heuristic metrics remain the explainable layer
- if OpenAI is unavailable, the API still returns all heuristic results cleanly

## Project Status

This submission is currently optimized for:

- Stripe Track
- Best Use of OpenAI API
