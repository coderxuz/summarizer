from aiogram.types import ReplyKeyboardMarkup,KeyboardButton

from app.services.translations import get_translations

async def lang_keyboards()->ReplyKeyboardMarkup:
    # Create a button for "O'zbek" language
    uzbek = KeyboardButton(text="O'zbek")
    english = KeyboardButton(text="English")
    russian = KeyboardButton(text="Русский")
    
    # Create the reply keyboard with the buttons
    keyboards = ReplyKeyboardMarkup(
        keyboard=[[english], [uzbek], [russian]],  # Each button on a new line
        resize_keyboard=True  # Automatically resize buttons to fit the screen
    )
    
    return keyboards

async def main_manu(lang_code:str)->ReplyKeyboardMarkup:
    change_lang = KeyboardButton(text=get_translations(lang=lang_code,key='choose_lang'))
    help = KeyboardButton(text=get_translations(lang=lang_code,key='help_txt'))
    
    keyboards = ReplyKeyboardMarkup(
        keyboard=[[change_lang,help]],
        resize_keyboard=True
    )
    return keyboards