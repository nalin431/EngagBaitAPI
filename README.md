# Engagement Bait API

Six interpretable metrics. One POST request. No black box.

Analyze structural engagement-bait patterns in text with a lightweight, deterministic heuristic layer and an optional OpenAI embedding-based semantic score. Every score includes a full transparent breakdown showing exactly which signals were detected and how they contributed.

## Live API

The API is publicly hosted and ready to use — no setup required.

| Resource | URL |
|---|---|
| Base URL | `https://engagbaitapi.onrender.com` |
| Interactive demo | https://engagbaitapi.onrender.com/demo |
| API Documentation | https://engagbaitapi.onrender.com/redoc |
| Health check | https://engagbaitapi.onrender.com/health |

Try it immediately with curl. Windows users, do NOT run this in Command Prompt or PowerShell. Use Git Bash, WSL, or a Unix-based terminal:

```bash
curl -s -X POST "https://engagbaitapi.onrender.com/analyze?embeddings=false" \
  -H "Content-Type: application/json" \
  -d '{"text": "Act now. This is your last chance to see the truth before it disappears. Everyone knows they are lying, and if you do not share this immediately, more people will be fooled. There is no middle ground, and the answer is obvious."}' \
  | python -m json.tool
```

## Use Cases

- **Social media moderation** — flag posts for editorial review before they gain traction
- **Journalism analytics** — scan articles for one-sided framing, rhetorical pressure, and emotional manipulation signals
- **Email filtering** — supplement spam detection with engagement-bait signals like urgency and curiosity gaps
- **Browser extension backend** — score articles inline as users read them
- **Media literacy education** — show students exactly why a text scores high, signal by signal

## How Each Metric Works

All scores are in the range `[0.0, 1.0]`. Two metrics (`evidence_density` and `counterargument_absence`) are **inverted** — higher values indicate more bait-like behavior, not more evidence or more nuance.

### Urgency Pressure

Scans for three categories of urgency signal using a curated phrase list:

- `time_pressure` — "act now", "last chance", "breaking", "tick tock"
- `scarcity` — "while supplies last", "limited spots", "only a few left"
- `fomo` — "don't miss out", "everyone already knows", "you'll regret this"

Score is the weighted average of the three sub-scores. Includes negation detection — "you don't need to act now" is not counted as urgency pressure.

### Evidence Density *(inverted — higher = less evidence)*

Looks for signals that a text is grounding its claims in data. Higher score means less evidence present.

- `citations` — "according to", "researchers found", "a study shows"
- `stats` — numeric patterns with units or percentages (e.g., "14 percent", "3.2 million")
- `external_sources` — named institutions, publications, or proper sourcing language

A text making bold claims with no data or sourcing scores close to 1.0.

### Arousal Intensity

Six sub-scores measuring emotional and rhetorical heat:

- `emotion_words` — curated lexicon with valence tiers: tier 1 (worried, angry), tier 2 (furious, hatred), tier 3 (enraged, terror). Higher tiers contribute more. Includes negation detection ("not angry" → no hit) and degree modifier scaling ("extremely angry" scores higher than "slightly angry").
- `moralized_language` — words framing issues in moral absolutes: corrupt, evil, sacred, betrayal
- `superlative_density` — "the worst", "ever", "unprecedented", "most dangerous"
- `caps_ratio` — proportion of ALL-CAPS words (checked on original, unmodified text)
- `exclamation_density` and `question_density` — scaled by text length to avoid false positives on short texts; a single `!` in a short email does not spike the score to 1.0
- `curiosity_gap` — "what they don't want you to know", "the real reason", "suppressed for years"

### Counterargument Absence *(inverted — higher = fewer concessions)*

Checks for the absence of language that acknowledges complexity or competing views.

- `tradeoff_absence` — missing: "on the other hand", "however", "that said", "the downside is"
- `conditional_absence` — missing: "it depends", "evidence suggests", "in some cases", "tends to"

A text presenting only one perspective with no hedging or qualification scores 1.0.

### Claim Volume vs Depth

Three sub-scores measuring whether a text makes many claims without explaining them:

- `claims_per_word` — assertion verbs (proves, reveals, exposes, confirms) relative to total word count
- `explanation_depth` — subordinate clauses and causal connectors (because, therefore, which means, as a result). More explanation lowers this sub-score.
- `listicle` — numbered or bulleted list structures, which tend to prioritize volume of points over depth of reasoning

### Lexical Diversity

Uses **MATTR** (Moving Average Type-Token Ratio) rather than raw TTR. A sliding window scans across the token sequence and computes `unique / window` at each position; the final score is the average across all windows. This is length-invariant — a 500-word repetitive text and a 50-word repetitive text are judged comparably. Window size adapts for short texts.

Inverted: low vocabulary diversity (sloganeering, repetition) scores high as a bait signal.

- `mattr` — moving average type-token ratio
- `type_token_ratio` — total unique words / total words

### Engagement Bait Score *(optional embeddings)*

When embeddings mode is enabled, the text is embedded using OpenAI `text-embedding-3-small` and scored against precomputed centroids of curated bait and neutral seed examples. **Centroids are computed once on the first embeddings request and cached for the server's lifetime** — subsequent calls do not re-embed the seed examples. Score is the transformed cosine similarity difference (bait centroid vs neutral centroid), normalized to 0–1.

This is the only metric that makes an external API call. If OpenAI is unavailable, `engagement_bait_score` returns `null` and all heuristic metrics still return normally.

## Tech Stack

- **FastAPI** — async Python web framework; chosen for automatic OpenAPI schema generation, which drives both the Swagger (`/docs`) and ReDoc (`/redoc`) documentation pages with zero extra configuration
- **Pydantic** — data validation layer; enforces strict input constraints (text length, batch size) and returns structured, descriptive error messages on every bad request
- **Python 3.10+** — all heuristic analyzers are pure stdlib Python with no heavy NLP dependencies, keeping the install footprint small and the analysis path fully auditable
- **OpenAI `text-embedding-3-small`** — lightweight, cost-efficient embedding model used for the optional semantic scoring layer; isolated from the heuristic path so the API degrades gracefully when unavailable
- **`python-dotenv`** — loads `OPENAI_API_KEY` from a local `.env` file for development; production key is set via Render environment variables
- **Render** — zero-config deployment from GitHub; auto-deploys on push, keeps the API publicly accessible without any infrastructure management

## API Guarantees

- **Idempotent** — heuristic scores are fully deterministic. The same text submitted twice will always return the exact same six scores and breakdowns, with no randomness or model state involved.
- **Stateful embeddings warm-up** — on the first request with embeddings enabled, the server embeds a small set of curated seed examples and caches the resulting bait and neutral centroids in memory. Every subsequent embeddings request uses those cached centroids — no repeated seed embedding calls. The `/health` endpoint exposes whether the OpenAI path is live.
- **Graceful degradation** — if OpenAI is unavailable or the key is missing, all six heuristic metrics still return normally. The `meta` object in every response reports exactly what ran and why.

## Quick Start

### Hosted (no setup)

The API is live at `https://engagbaitapi.onrender.com`. No API key or installation needed for heuristic scoring.

```bash
# Health check
curl https://engagbaitapi.onrender.com/health

# Analyze text (heuristics only)
curl -s -X POST "https://engagbaitapi.onrender.com/analyze?embeddings=false" -H "Content-Type: application/json" -d '{"text": "Act now. This is your last chance to see the truth before it disappears. Everyone knows they are lying, and if you do not share this immediately, more people will be fooled. There is no middle ground, and the answer is obvious."}'

# Analyze text with embeddings score
curl -s -X POST "https://engagbaitapi.onrender.com/analyze?embeddings=true" -H "Content-Type: application/json" -d '{"text": "Act now. This is your last chance to see the truth before it disappears. Everyone knows they are lying, and if you do not share this immediately, more people will be fooled. There is no middle ground, and the answer is obvious."}'
```

### Run Locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

Local configuration:

1. Copy `.env.example` to `.env`
2. Add your `OPENAI_API_KEY` (required only for embeddings scoring)

Local URLs:

- API: `http://localhost:5000`
- Docs: `http://localhost:5000/docs`
- Demo: `http://localhost:5000/demo`

## Endpoints

Base URL: `https://engagbaitapi.onrender.com`

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

Example (curl):

```bash
curl -s -X POST "https://engagbaitapi.onrender.com/analyze?embeddings=false" \
  -H "Content-Type: application/json" \
  -d '{"text": "Act now. This is your last chance to see the truth before it disappears. Everyone knows they are lying, and if you do not share this immediately, more people will be fooled. There is no middle ground, and the answer is obvious."}'
```

Example (PowerShell, local):

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
  "lexical_diversity": {
    "score": 0.21,
    "breakdown": {
      "mattr": 0.79,
      "type_token_ratio": 0.79
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

Submit up to 10 texts in one request. The response preserves submission order and includes each caller-supplied `id`.

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

Example (curl):

```bash
curl -s -X POST "https://engagbaitapi.onrender.com/analyze/batch?embeddings=false" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": "bait", "text": "Act now. This is your last chance to see the truth before it disappears. Everyone knows they are lying, and if you do not share this immediately, more people will be fooled. There is no middle ground, and the answer is obvious."},
      {"id": "neutral", "text": "A review of three transit funding proposals found that ridership increased between 12 and 18 percent in pilot cities. The report recommends further study before statewide adoption and notes that two of the five authors issued a minority opinion citing timeline risks."}
    ]
  }'
```

## Error Reference

All validation errors return `HTTP 422` with this shape:

```json
{"detail": "...", "field": "..."}
```

| Trigger | `detail` value |
|---|---|
| text under 50 characters | `"Text must be at least 50 characters (got N)"` |
| text over 50,000 characters | `"Text must be at most 50000 characters (got N)"` |
| empty batch | `"Batch must include at least 1 item"` |
| batch over 10 items | `"Batch must include at most 10 items"` |

## Response Meta

The `meta` object is included in every response and reports the state of the embeddings path:

```json
"meta": {
  "embeddings_requested": true,
  "embeddings_used": false,
  "openai_available": false,
  "vector_backend": "none"
}
```

Field meanings:

- `embeddings_requested` — whether the request asked for embeddings scoring
- `embeddings_used` — whether the embeddings path actually ran
- `openai_available` — whether the server has a valid OpenAI key configured
- `vector_backend` — `none` (heuristic only) or `centroid` (embeddings used)

## Browser Demo

Live demo: **https://engagbaitapi.onrender.com/demo**

Locally: `GET /demo`

It includes:

- paste-in text analysis
- a `Use Embeddings` toggle
- three sample inputs: high bait, neutral, and mixed text
- score cards for all six metrics
- raw JSON output for developer inspection

## Embeddings

The OpenAI portion of the project is intentionally narrow and opt-in:

- embeddings power `engagement_bait_score` only
- the scorer uses centroid similarity over curated bait and neutral seed examples
- centroids are computed once on first use and cached in memory for the server's lifetime
- heuristic metrics remain the explainable, deterministic layer
- if OpenAI is unavailable, the API still returns all heuristic results cleanly and reports the reason in `meta`

## Embeddings Benchmark

The project includes an internal benchmark runner for reviewing embeddings behavior on curated examples.

Run:

```bash
python -m scripts.run_ml_benchmark
```

Requirements:

- a valid `OPENAI_API_KEY`
- benchmark examples in `data/ml_benchmark_examples.json`

The script prints per-example: id, label, embeddings score, all heuristic scores, response metadata, and notes for manual review.

This is a manual evaluation tool, not a normal CI test.

## Testing

Run the automated tests with:

```bash
python -m pytest -q
```

## What It Does Not Do

- Fact check claims
- Classify political ideology
- Detect truthfulness
- Perform content moderation

The heuristic metrics are transparent signal extractors, not a unified engagement bait score. They are intentionally kept separate so callers can interpret each signal on its own terms.

## Project Status

This submission is currently optimized for:

- Stripe Track
- Best Use of OpenAI API
