import gc
from abc import ABC, abstractmethod
from typing import List

import torch


class BaseTranslator(ABC):
    def __init__(self, model_name: str, device: str = "auto"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def load_model(self) -> None: ...

    @abstractmethod
    def translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        """Args:
        text: 待翻译文本
        src_lang: 源语言代码 (ISO 639-1, 如 "zh", "en")
        tgt_lang: 目标语言代码
        """

    def translate_batch(
        self, texts: List[str], src_lang: str, tgt_lang: str
    ) -> List[str]:
        return [self.translate(text, src_lang, tgt_lang) for text in texts]

    def _log_device_info(self) -> None:
        if self.model is None:
            return
        param_device = next(self.model.parameters()).device
        param_dtype = next(self.model.parameters()).dtype
        print(f"  -> {self.name} loaded on: {param_device} ({param_dtype})")

    def unload_model(self) -> None:
        self.model = None
        self.tokenizer = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def _resolve_device(self) -> torch.device:
        if self.device != "auto":
            return torch.device(self.device)
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name})"
