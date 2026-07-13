"""
Translation endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from deep_translator import GoogleTranslator

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


class TranslationRequest(BaseModel):
    text: str
    target_language: str


@router.get("/languages")
def get_supported_languages():
    """Get list of supported languages"""
    return SUPPORTED_LANGUAGES


@router.post("")
def translate_text(request: TranslationRequest):
    """Translate text to the target language"""
    if request.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {request.target_language}"
        )

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        translator = GoogleTranslator(source="auto", target=request.target_language)
        translated = translator.translate(request.text)
        return {
            "original": request.text,
            "translated": translated,
            "target_language": request.target_language,
            "target_language_name": SUPPORTED_LANGUAGES[request.target_language],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
