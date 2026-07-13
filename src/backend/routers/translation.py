"""
Translation endpoints for the High School Management System API
"""

import logging
import threading
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/translate",
    tags=["translation"]
)

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
    "zh-CN": "Chinese (Simplified)",
    "pt": "Portuguese",
    "it": "Italian",
    "ko": "Korean",
    "ar": "Arabic",
    "ru": "Russian",
    "hi": "Hindi",
}

# Thread-safe cache of translator instances per target language
_translator_cache: dict[str, GoogleTranslator] = {}
_cache_lock = threading.Lock()


def get_translator(target_language: str) -> GoogleTranslator:
    """Return a cached GoogleTranslator for the given target language."""
    with _cache_lock:
        if target_language not in _translator_cache:
            _translator_cache[target_language] = GoogleTranslator(
                source="auto", target=target_language
            )
        return _translator_cache[target_language]


class TranslationRequest(BaseModel):
    text: str
    target_language: str


class BatchTranslationRequest(BaseModel):
    texts: List[str]
    target_language: str


@router.get("/languages")
def get_supported_languages():
    """Get list of supported languages"""
    return SUPPORTED_LANGUAGES


@router.post("")
def translate_text(request: TranslationRequest):
    """Translate a single text to the target language"""
    if request.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {request.target_language}"
        )

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        translator = get_translator(request.target_language)
        translated = translator.translate(request.text)
        return {
            "original": request.text,
            "translated": translated,
            "target_language": request.target_language,
            "target_language_name": SUPPORTED_LANGUAGES[request.target_language],
        }
    except Exception as e:
        logger.error("Translation failed for language %s: %s", request.target_language, e)
        raise HTTPException(
            status_code=500,
            detail="Translation service temporarily unavailable"
        )


@router.post("/batch")
def translate_batch(request: BatchTranslationRequest):
    """Translate a list of texts to the target language in one request"""
    if request.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {request.target_language}"
        )

    if not request.texts:
        raise HTTPException(status_code=400, detail="Texts list cannot be empty")

    try:
        translator = get_translator(request.target_language)
        translated_texts = [
            translator.translate(text) if text.strip() else text
            for text in request.texts
        ]
        return {
            "translated": translated_texts,
            "target_language": request.target_language,
            "target_language_name": SUPPORTED_LANGUAGES[request.target_language],
        }
    except Exception as e:
        logger.error("Batch translation failed for language %s: %s", request.target_language, e)
        raise HTTPException(
            status_code=500,
            detail="Translation service temporarily unavailable"
        )
