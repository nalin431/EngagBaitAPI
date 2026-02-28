"""
Seed Actian VectorAI DB with embedded seed examples.

Run once at setup or deployment when USE_ACTIAN=true.
Requires: OPENAI_API_KEY, ACTIAN_* env vars.

Usage: python -m scripts.seed_actian
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ml.embeddings import get_embedding
from app.ml.vector_store import init_vector_store, upsert_examples


def main() -> int:
    if not os.environ.get("OPENAI_API_KEY", "").strip().startswith("sk-"):
        print("OPENAI_API_KEY not set; cannot embed examples.")
        return 1
    if not init_vector_store():
        print("Actian VectorAI DB not available. Set USE_ACTIAN=true and ACTIAN_* vars.")
        return 1

    path = Path(__file__).resolve().parent.parent / "data" / "seed_examples.json"
    if not path.exists():
        print(f"Seed examples not found: {path}")
        return 1

    with path.open() as f:
        examples = json.load(f)

    texts = [ex["text"] for ex in examples]
    labels = [ex["label"] for ex in examples]

    embeddings: list[list[float]] = []
    for i, text in enumerate(texts):
        emb = get_embedding(text)
        if emb is None:
            print(f"Failed to embed example {i + 1}")
            return 1
        embeddings.append(emb)

    if upsert_examples(embeddings, labels, texts):
        print(f"Upserted {len(examples)} examples into Actian VectorAI DB.")
        return 0
    print("Upsert failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
