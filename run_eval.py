from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from evaluation.runner import evaluate_model, load_test_cases, print_comparison
from scoring import ScoringManager


def main():
    parser = argparse.ArgumentParser(description="Translation model evaluation")
    parser.add_argument(
        "--config", default="config/models.yaml", help="Model config file"
    )
    parser.add_argument(
        "--scoring-config",
        default="config/scoring.yaml",
        help="Scoring config file",
    )
    parser.add_argument(
        "--data", default="data/test_samples.json", help="Test data file"
    )
    parser.add_argument(
        "--models", nargs="*", help="Specific model IDs to evaluate (default: all)"
    )
    parser.add_argument(
        "--output", default="results", help="Output directory for results"
    )
    parser.add_argument(
        "--no-score",
        action="store_true",
        help="Disable LLM scoring even if configured",
    )
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    scoring_config = (
        None if args.no_score else _load_scoring_config(args.scoring_config)
    )
    scoring_manager = ScoringManager(scoring_config)
    if scoring_manager.has_services:
        print(f"LLM scoring enabled with {len(scoring_manager.services)} provider(s)")
    else:
        print("LLM scoring disabled")

    test_cases = load_test_cases(args.data)
    print(f"Loaded {len(test_cases)} test cases")

    models = config["models"]
    if args.models:
        models = {k: v for k, v in models.items() if k in args.models}

    if not models:
        print("No models to evaluate. Check --models filter or config file.")
        sys.exit(1)

    print(f"Models to evaluate: {list(models.keys())}")

    results_dir = Path(args.output)
    results_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    for model_config in models.values():
        summary = evaluate_model(model_config, test_cases, results_dir, scoring_manager)
        summaries.append(summary)

    print_comparison(summaries)

    comparison = [{k: v for k, v in s.items() if k != "details"} for s in summaries]
    comparison_file = results_dir / "comparison.json"
    with open(comparison_file, "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)

    print(f"\nDetailed results saved to {results_dir}/")


def _load_scoring_config(path: str) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("scoring", None) if data else None
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    main()
