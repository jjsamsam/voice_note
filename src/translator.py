"""
Translation Module
Translates text using Google Translate via deep-translator.
"""

from deep_translator import GoogleTranslator


# Common languages with their display names (Korean)
SUPPORTED_LANGUAGES = {
    "ko": "한국어",
    "en": "English",
    "ja": "日本語",
    "zh-CN": "中文 (简体)",
    "zh-TW": "中文 (繁體)",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "pt": "Português",
    "ru": "Русский",
    "it": "Italiano",
    "vi": "Tiếng Việt",
    "th": "ไทย",
    "ar": "العربية",
    "hi": "हिन्दी",
}


def translate(text, source="auto", target="ko"):
    """
    Translate text from source language to target language.

    Args:
        text: Text to translate
        source: Source language code ('auto' for auto-detect)
        target: Target language code

    Returns:
        Translated text string
    """
    if not text or not text.strip():
        return ""

    translator = GoogleTranslator(source=source, target=target)

    # deep-translator has a 5000 char limit per request
    max_chunk = 4500
    if len(text) <= max_chunk:
        return translator.translate(text)

    # Split long text into chunks
    chunks = []
    sentences = text.replace(". ", ".\n").split("\n")
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chunk:
            current_chunk += sentence + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    translated_chunks = [translator.translate(chunk) for chunk in chunks]
    return " ".join(translated_chunks)


def get_supported_languages():
    """Return the dictionary of supported languages."""
    return SUPPORTED_LANGUAGES.copy()
