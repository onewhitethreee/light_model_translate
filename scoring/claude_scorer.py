from __future__ import annotations

import os

import anthropic

from .base import BaseScoringService


class ClaudeScoringService(BaseScoringService):
    def __init__(self, model: str, api_base: str):
        super().__init__(model, api_base)
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = anthropic.Anthropic(api_key=api_key, base_url=api_base)

    @property
    def provider_name(self) -> str:
        return "claude"

    def _call_api(self, prompt: str) -> str | None:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=256,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
