from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

import torch

from utils.lang_codes import get_nllb_lang_code

from .base import BaseTranslator


class NLLBTranslator(BaseTranslator):
    @property
    def name(self) -> str:
        return f"NLLB ({self.model_name.split('/')[-1]})"

    def load_model(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name,
            dtype=torch.float16,
            device_map="auto",
            tie_word_embeddings=False,
        )
        self.model.eval()
        self._log_device_info()

    def translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        src_code = get_nllb_lang_code(src_lang)
        tgt_code = get_nllb_lang_code(tgt_lang)

        self.tokenizer.src_lang = src_code
        inputs = self.tokenizer(
            text, return_tensors="pt", max_length=512, truncation=True
        ).to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(tgt_code),
            max_new_tokens=512,
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
