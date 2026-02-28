"""
Run the held-out ML benchmark against the live OpenAI scoring path.

Usage:
    python -m scripts.run_ml_benchmark
"""

import json
import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.analyzers import analyze_text


def _require_openai_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key.startswith("sk-"):
        print(
            "OPENAI_API_KEY is not set or invalid. "
            "Live benchmark evaluation requires a valid OpenAI key."
        )
        raise SystemExit(1)
    return key


def _load_benchmark() -> list[dict[str, str]]:
    path = Path(__file__).resolve().parent.parent / "data" / "ml_benchmark_examples.json"
    if not path.exists():
        print(f"Benchmark file not found: {path}")
        raise SystemExit(1)
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _score_summary(result) -> str:
    return (
        f"urgency={result.urgency_pressure.score:.2f} | "
        f"low_evidence={result.evidence_density.score:.2f} | "
        f"arousal={result.arousal_intensity.score:.2f} | "
        f"counterargument_absence={result.counterargument_absence.score:.2f} | "
        f"claim_volume={result.claim_volume_vs_depth.score:.2f}"
    )


def main() -> int:
    _require_openai_key()
    benchmark = _load_benchmark()

    print("Engagement Bait API ML Benchmark")
    print(f"Examples: {len(benchmark)}")
    print("-" * 72)

    for item in benchmark:
        result = analyze_text(item["text"], ml=True)
        print(f"{item['id']} [{item['label']}]")
        print(
            f"Expected: ml={item['expected_ml_behavior']} | "
            f"heuristics={item['expected_heuristic_behavior']}"
        )
        print(f"ML score: {result.engagement_bait_score}")
        print(f"Heuristics: {_score_summary(result)}")
        print(
            "Meta: "
            f"ml_requested={result.meta.ml_requested}, "
            f"ml_used={result.meta.ml_used}, "
            f"openai_available={result.meta.openai_available}, "
            f"vector_backend={result.meta.vector_backend}"
        )
        print(f"Notes: {item['notes']}")
        print("-" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
