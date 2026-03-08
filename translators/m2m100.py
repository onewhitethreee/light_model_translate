from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

import torch

from utils.lang_codes import get_m2m100_lang_code

from .base import BaseTranslator


class M2M100Translator(BaseTranslator):
    @property
    def name(self) -> str:
        return f"M2M-100 ({self.model_name.split('/')[-1]})"

    def load_model(self) -> None:
        self.tokenizer = M2M100Tokenizer.from_pretrained(self.model_name)
        self.model = M2M100ForConditionalGeneration.from_pretrained(
            self.model_name,
            dtype=torch.float16,
            device_map="auto",
        )
        self.model.eval()
        self._log_device_info()

    def translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        src_code = get_m2m100_lang_code(src_lang)
        tgt_code = get_m2m100_lang_code(tgt_lang)

        self.tokenizer.src_lang = src_code
        inputs = self.tokenizer(
            text, return_tensors="pt", max_length=512, truncation=True
        ).to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.get_lang_id(tgt_code),
            max_new_tokens=512,
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
