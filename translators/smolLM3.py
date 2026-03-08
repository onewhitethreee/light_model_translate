from transformers import AutoModelForCausalLM, AutoTokenizer

from utils.lang_codes import get_language_name

from .base import BaseTranslator

SYSTEM_PROMPT = (
    "You are a professional translator. "
    "Translate accurately and naturally. "
    "Output only the translation, nothing else."
)

class SmolLMTranslator(BaseTranslator):
    @property
    def name(self) -> str:
        return f"SmolLM ({self.model_name.split('/')[-1]})"

    def load_model(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype="auto",
        )
        self.model.eval()
        self._log_device_info()

    def translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        src_code = get_language_name(src_lang)
        tgt_code = get_language_name(tgt_lang)
        user_prompt = (
            f"Translate the following {src_code} text to {tgt_code}. "
            f"Output ONLY the translation, nothing else.\n\n{text}"
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        input_text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,
        )
        generated_ids = outputs[0][inputs["input_ids"].shape[-1] :]
        return self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    
