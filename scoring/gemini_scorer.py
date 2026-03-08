from __future__ import annotations

import os

from google import genai
from google.genai import types

from .base import BaseScoringService


class GeminiScoringService(BaseScoringService):
    def __init__(self, model: str, api_base: str):
        super().__init__(model, api_base)
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.client = genai.Client(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _call_api(self, prompt: str) -> str | None:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=256,
            ),
        )
        return response.text
