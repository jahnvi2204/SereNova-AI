"""
Optional RAGAS evaluation against a tiny gold set (faithfulness / answer relevancy).
Requires GEMINI_API_KEY and: pip install ragas datasets langchain-google-genai
Run from backend/:  python scripts/ragas_eval.py
"""
from __future__ import annotations

import os
import sys

# Ensure backend root is on path
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def main() -> None:
    from config import Config

    if not (Config.GEMINI_API_KEY or "").strip():
        print("Set GEMINI_API_KEY in .env for RAGAS LLM-as-judge.")
        sys.exit(1)

    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import answer_relevancy, faithfulness
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as e:
        print("Missing dependency:", e)
        sys.exit(1)

    # Toy example: question, ground-truth context chunk, model answer
    data = {
        "question": [
            "What is a grounding technique for anxiety?",
        ],
        "answer": [
            "Name five things you can see, four you can feel, three you hear, two you smell, and one you taste to anchor in the present.",
        ],
        "contexts": [
            [
                "5-4-3-2-1 grounding helps orient attention to the present using senses during anxiety or dissociation."
            ],
        ],
    }
    ds = Dataset.from_dict(data)

    llm = ChatGoogleGenerativeAI(
        model=Config.GEMINI_MODEL_NAME,
        google_api_key=Config.GEMINI_API_KEY,
        temperature=0.0,
    )
    res = evaluate(ds, metrics=[faithfulness, answer_relevancy], llm=llm)
    print(res)
    out = "ragas_result.csv"
    try:
        res.to_pandas().to_csv(out, index=False)
    except Exception as exc:  # noqa: BLE001
        print("Could not export CSV (ragas version mismatch?):", exc)
    else:
        print("Wrote", out)


if __name__ == "__main__":
    main()
