from aiogram.types import Message
from googletrans import Translator

import aiogram.types as types

import json

with open("translations.json", "r", encoding="utf-8") as file:
    translations = json.load(file)


def get_translations(lang, key):
    return translations.get(lang, {}).get(key, translations["ru"].get(key))

async def get_use_lang(query_or_message, user_data):
    # Check if the input is a CallbackQuery or a Message
    if isinstance(query_or_message, Message):
        lang_code = query_or_message.from_user.language_code
    elif isinstance(query_or_message, types.CallbackQuery):
        # Use `query_or_message.message.from_user.language_code` for CallbackQuery
        lang_code = query_or_message.message.from_user.language_code
    else:
        # Default to an empty string if the type is unexpected
        lang_code = None

    # Return user language preference or detected language
    return (
        user_data.get("lang") if user_data.get("lang") else lang_code
    )

async def translate_text(text: str, target_language: str) -> str:
    """Translate the text to the target language."""
    if not text:
        return "Error: No text provided for translation."
    
    translator = Translator()
    try:
        # Translate the text
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        return f"Error while translating: {str(e)}"