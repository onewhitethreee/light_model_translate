NLLB_LANG_MAP = {
    "zh": "zho_Hans",
    "en": "eng_Latn",
    "ja": "jpn_Jpan",
    "ko": "kor_Hang",
    "fr": "fra_Latn",
    "de": "deu_Latn",
    "es": "spa_Latn",
    "ru": "rus_Cyrl",
    "ar": "arb_Arab",
    "pt": "por_Latn",
    "it": "ita_Latn",
    "th": "tha_Thai",
    "vi": "vie_Latn",
}

M2M100_LANG_MAP = {
    "zh": "zh",
    "en": "en",
    "ja": "ja",
    "ko": "ko",
    "fr": "fr",
    "de": "de",
    "es": "es",
    "ru": "ru",
    "ar": "ar",
    "pt": "pt",
    "it": "it",
    "th": "th",
    "vi": "vi",
}

LANGUAGE_NAMES = {
    "zh": "Chinese",
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
    "ar": "Arabic",
    "pt": "Portuguese",
    "it": "Italian",
    "th": "Thai",
    "vi": "Vietnamese",
}


def get_nllb_lang_code(lang: str) -> str:
    if lang in NLLB_LANG_MAP:
        return NLLB_LANG_MAP[lang]
    raise ValueError(
        f"Unsupported language for NLLB: {lang}. "
        f"Available: {list(NLLB_LANG_MAP.keys())}"
    )


def get_m2m100_lang_code(lang: str) -> str:
    if lang in M2M100_LANG_MAP:
        return M2M100_LANG_MAP[lang]
    raise ValueError(
        f"Unsupported language for M2M-100: {lang}. "
        f"Available: {list(M2M100_LANG_MAP.keys())}"
    )


def get_language_name(lang: str) -> str:
    return LANGUAGE_NAMES.get(lang, lang)
