from __future__ import annotations

import os

from openai import OpenAI

from .base import BaseScoringService

SYSTEM_MESSAGE = "You are a translation quality evaluator. Respond only with JSON."


class DeepSeekScoringService(BaseScoringService):
    def __init__(self, model: str, api_base: str):
        super().__init__(model, api_base)
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key, base_url=api_base)

    @property
    def provider_name(self) -> str:
        return "deepseek"

    def _call_api(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=256,
        )
        return response.choices[0].message.content or ""
