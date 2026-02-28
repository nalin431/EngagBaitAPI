# Engagement Bait API

Detect structural manipulation in text: urgency pressure, evidence density, overconfidence, arousal, in-group/out-group markers, narrative simplification, and claim volume vs depth. Built for HackIllinois 2026 (Stripe Track).

## Tech Stack

- **FastAPI** – HTTP API, auto OpenAPI docs
- **Python 3.10+**
- **Pydantic** – request/response validation

## Quick Start

```bash
# Create venv (optional)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS

# Install
pip install -r requirements.txt

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
  "overconfidence": { "score": 0.85, "breakdown": { "absolutist": 0.9, "strong_modals": 0.8, "hedging_absence": 0.85, "predictive_unqualified": 0.8 } },
  "arousal_intensity": { "score": 0.7, "breakdown": { "emotion_words": 0.75, "exclamation_density": 0.6, "moralized_language": 0.8 } },
  "ingroup_outgroup": { "score": 0.65, "breakdown": { "us_them_markers": 0.7, "tribal_language": 0.6 } },
  "narrative_simplification": { "score": 0.8, "breakdown": { "binary_connectors": 0.85, "single_cause": 0.9, "tradeoff_absence": 0.7, "conditional_absence": 0.75 } },
  "claim_volume_vs_depth": { "score": 0.6, "breakdown": { "claims_per_word": 0.65, "explanation_depth": 0.55 } }
}
```

## Metrics

| Metric | Sub-metrics | Description |
|--------|-------------|-------------|
| **Urgency Pressure** | time_pressure, scarcity, fomo | Time pressure, scarcity, FOMO phrases |
| **Evidence Density** | citations, stats, external_sources | Inverted: low evidence → high score |
| **Overconfidence** | absolutist, strong_modals, hedging_absence, predictive_unqualified | Absolutist language, strong modals, no hedging |
| **Arousal Intensity** | emotion_words, exclamation_density, moralized_language | High-arousal emotions, exclamations, moralized terms |
| **In-group/Out-group** | us_them_markers, tribal_language | We/they, tribal labels |
| **Narrative Simplification** | binary_connectors, single_cause, tradeoff_absence, conditional_absence | Either/or, single cause, no trade-offs |
| **Claim Volume vs Depth** | claims_per_word, explanation_depth | Many claims, shallow explanation |

## Error Responses

- **422 Unprocessable Entity** – Invalid input (e.g., text too short/long)
- **500 Internal Server Error** – Server error

## License

MIT
