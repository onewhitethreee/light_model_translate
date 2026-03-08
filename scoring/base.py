from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from utils.lang_codes import get_language_name

SCORING_PROMPT_TEMPLATE = """\
You are a professional translation quality evaluator.

Score the following machine translation on a scale of 1-10.

Source text ({src_lang_name}):
{source}

Reference translation ({tgt_lang_name}):
{reference}

Machine translation to evaluate:
{translation}

Evaluation criteria:
- Accuracy: Does the translation convey the same meaning as the source?
- Fluency: Is the translation natural and grammatically correct in the target language?
- Terminology: Are technical terms, proper nouns, and domain-specific vocabulary handled correctly?

Respond with ONLY a JSON object in this exact format, nothing else:
{{"score": <number from 1 to 10>, "explanation": "<brief explanation in English>"}}\
"""


@dataclass
class ScoringResult:
    score: float
    explanation: str
    provider: str
    model: str


class BaseScoringService(ABC):
    def __init__(self, model: str, api_base: str):
        self.model = model
        self.api_base = api_base

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    def _call_api(self, prompt: str) -> str:
        """Call the LLM API and return raw response text."""
        ...

    def score(
        self,
        source: str,
        reference: str,
        translation: str,
        src_lang: str,
        tgt_lang: str,
    ) -> ScoringResult:
        prompt = SCORING_PROMPT_TEMPLATE.format(
            src_lang_name=get_language_name(src_lang),
            tgt_lang_name=get_language_name(tgt_lang),
            source=source,
            reference=reference,
            translation=translation,
        )

        try:
            raw = self._call_api(prompt)
            parsed = self._parse_response(raw)
            return ScoringResult(
                score=parsed["score"],
                explanation=parsed["explanation"],
                provider=self.provider_name,
                model=self.model,
            )
        except Exception as e:
            return ScoringResult(
                score=0.0,
                explanation=f"[ERROR] {e}",
                provider=self.provider_name,
                model=self.model,
            )

    @staticmethod
    def _parse_response(raw: str) -> dict:
        text = raw.strip()

        # Try direct JSON parse
        try:
            data = json.loads(text)
            return {
                "score": float(data["score"]),
                "explanation": str(data["explanation"]),
            }
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

        # Try extracting JSON from markdown code block
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return {
                    "score": float(data["score"]),
                    "explanation": str(data["explanation"]),
                }
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

        # Try finding any JSON-like object with "score" key
        match = re.search(r'\{[^{}]*"score"[^{}]*\}', text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return {
                    "score": float(data["score"]),
                    "explanation": str(data["explanation"]),
                }
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

        raise ValueError(f"Failed to parse scoring response: {text[:200]}")
