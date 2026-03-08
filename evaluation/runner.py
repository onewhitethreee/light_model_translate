from __future__ import annotations

import json
import time
from pathlib import Path

from tabulate import tabulate
from tqdm import tqdm

from scoring import ScoringManager
from translators import create_translator

from .metrics import (
    compute_bleu,
    compute_chrf,
    compute_corpus_bleu,
    compute_corpus_chrf,
)


def load_test_cases(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_model(
    model_config: dict,
    test_cases: list,
    results_dir: Path,
    scoring_manager: ScoringManager | None = None,
) -> dict:
    model_type = model_config["type"]
    model_name = model_config["model_name"]

    print(f"\n{'=' * 60}")
    print(f"Evaluating: {model_name}")
    print(f"{'=' * 60}")

    translator = create_translator(model_type, model_name)

    print("Loading model...")
    load_start = time.time()
    translator.load_model()
    load_time = time.time() - load_start
    print(f"Model loaded in {load_time:.1f}s")

    results = []
    for case in tqdm(test_cases, desc="Translating"):
        start = time.time()
        try:
            translation = translator.translate(
                case["source"], case["src_lang"], case["tgt_lang"]
            )
            elapsed = time.time() - start

            bleu = compute_bleu(translation, case["reference"])
            chrf = compute_chrf(translation, case["reference"])

            entry = {
                "source": case["source"],
                "reference": case["reference"],
                "translation": translation,
                "src_lang": case["src_lang"],
                "tgt_lang": case["tgt_lang"],
                "bleu": round(bleu, 2),
                "chrf": round(chrf, 2),
                "time_seconds": round(elapsed, 3),
            }
            results.append(entry)
        except Exception as e:
            print(f"  Error: {e}")
            error_entry = {
                "source": case["source"],
                "reference": case["reference"],
                "translation": f"[ERROR] {e}",
                "src_lang": case["src_lang"],
                "tgt_lang": case["tgt_lang"],
                "bleu": 0.0,
                "chrf": 0.0,
                "time_seconds": 0.0,
            }
            results.append(error_entry)

    translator.unload_model()

    if scoring_manager and scoring_manager.has_services:
        print("Running LLM scoring...")
        for entry in tqdm(results, desc="Scoring"):
            if entry["translation"].startswith("[ERROR]"):
                continue
            score_results = scoring_manager.score(
                source=entry["source"],
                reference=entry["reference"],
                translation=entry["translation"],
                src_lang=entry["src_lang"],
                tgt_lang=entry["tgt_lang"],
            )
            entry["llm_scores"] = {
                r.provider: {
                    "score": r.score,
                    "explanation": r.explanation,
                    "model": r.model,
                }
                for r in score_results
            }
            entry["avg_llm_score"] = scoring_manager.average_score(score_results)

    valid_results = [r for r in results if not r["translation"].startswith("[ERROR]")]
    hypotheses = [r["translation"] for r in valid_results]
    references = [r["reference"] for r in valid_results]

    summary = {
        "model": translator.name,
        "model_name": model_name,
        "load_time_seconds": round(load_time, 1),
        "avg_bleu": _safe_avg([r["bleu"] for r in results]),
        "avg_chrf": _safe_avg([r["chrf"] for r in results]),
        "corpus_bleu": round(compute_corpus_bleu(hypotheses, references), 2)
        if hypotheses
        else 0,
        "corpus_chrf": round(compute_corpus_chrf(hypotheses, references), 2)
        if hypotheses
        else 0,
        "avg_time_seconds": _safe_avg([r["time_seconds"] for r in results], decimals=3),
        "total_samples": len(results),
        "errors": len(results) - len(valid_results),
        "details": results,
    }

    llm_scores = [r["avg_llm_score"] for r in results if "avg_llm_score" in r]
    if llm_scores:
        summary["avg_llm_score"] = _safe_avg(llm_scores)

    output_file = results_dir / f"{model_name.replace('/', '_')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return summary


def print_comparison(summaries: list[dict]) -> None:
    print(f"\n{'=' * 80}")
    print("EVALUATION RESULTS COMPARISON")
    print(f"{'=' * 80}")

    has_scoring = any("avg_llm_score" in s for s in summaries)

    headers = [
        "Model",
        "BLEU\n(avg)",
        "chrF\n(avg)",
        "BLEU\n(corpus)",
        "chrF\n(corpus)",
        "Avg Time\n(s)",
        "Load Time\n(s)",
        "Errors",
    ]
    if has_scoring:
        headers.append("LLM Score\n(avg)")

    rows = []
    for s in summaries:
        row = [
            s["model"],
            s["avg_bleu"],
            s["avg_chrf"],
            s["corpus_bleu"],
            s["corpus_chrf"],
            s["avg_time_seconds"],
            s["load_time_seconds"],
            s["errors"],
        ]
        if has_scoring:
            row.append(s.get("avg_llm_score", "-"))
        rows.append(row)

    print(tabulate(rows, headers=headers, tablefmt="grid"))


def _safe_avg(values: list[float], decimals: int = 2) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), decimals)
