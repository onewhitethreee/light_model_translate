from __future__ import annotations

from .base import BaseTranslator
from .m2m100 import M2M100Translator
from .nllb import NLLBTranslator
from .qwen import QwenTranslator
from .smolLM3 import SmolLMTranslator
TRANSLATOR_REGISTRY: dict[str, type[BaseTranslator]] = {
    "nllb": NLLBTranslator,
    "m2m100": M2M100Translator,
    "qwen": QwenTranslator,
    "smollm": SmolLMTranslator,
}


def create_translator(model_type: str, model_name: str, **kwargs) -> BaseTranslator:
    if model_type not in TRANSLATOR_REGISTRY:
        available = ", ".join(TRANSLATOR_REGISTRY.keys())
        raise ValueError(f"Unknown model type: {model_type}. Available: {available}")
    return TRANSLATOR_REGISTRY[model_type](model_name=model_name, **kwargs)
