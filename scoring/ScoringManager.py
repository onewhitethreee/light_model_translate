from __future__ import annotations

from .base import BaseScoringService, ScoringResult
from .claude_scorer import ClaudeScoringService
from .gemini_scorer import GeminiScoringService
from .openai_scorer import OpenAIScoringService
from .deepseek_scorer import DeepSeekScoringService

SCORER_REGISTRY: dict[str, type[BaseScoringService]] = {
    "claude": ClaudeScoringService,
    "gemini": GeminiScoringService,
    "openai": OpenAIScoringService,
    "deepseek": DeepSeekScoringService, 
}


class ScoringManager:
    def __init__(self, scoring_config: dict | None = None):
        self.services: list[BaseScoringService] = []
        if scoring_config:
            self._init_services(scoring_config)

    def _init_services(self, scoring_config: dict) -> None:
        for provider_name, provider_config in scoring_config.items():
            if not provider_config.get("enabled", False):
                continue

            scorer_cls = SCORER_REGISTRY.get(provider_name)
            if scorer_cls is None:
                print(
                    f"  Warning: Unknown scoring provider '{provider_name}', skipping"
                )
                continue

            try:
                scorer = scorer_cls(
                    model=provider_config["model"],
                    api_base=provider_config["api_base"],
                )
                self.services.append(scorer)
                print(
                    f"  Scoring service loaded: {provider_name} ({provider_config['model']})"
                )
            except Exception as e:
                print(f"  Warning: Failed to init {provider_name} scorer: {e}")

    @property
    def has_services(self) -> bool:
        return len(self.services) > 0

    def score(
        self,
        source: str,
        reference: str,
        translation: str,
        src_lang: str,
        tgt_lang: str,
    ) -> list[ScoringResult]:
        results = []
        for service in self.services:
            result = service.score(source, reference, translation, src_lang, tgt_lang)
            results.append(result)
        return results

    @staticmethod
    def average_score(results: list[ScoringResult]) -> float:
        valid = [r.score for r in results if r.score > 0]
        if not valid:
            return 0.0
        return round(sum(valid) / len(valid), 2)
