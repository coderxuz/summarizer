from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

async def start_inline_keyboard(lang:str,send_url:str,help_txt:str)->InlineKeyboardMarkup:
    choose_lang = InlineKeyboardButton(text=lang,callback_data='lang')
    send_youtube_video = InlineKeyboardButton(text=send_url,callback_data='send_url')
    help = InlineKeyboardButton(text=help_txt,callback_data='about')
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[choose_lang,send_youtube_video,help]],row_width=2)
    
    return keyboard

async def choose_lang_keyb()->InlineKeyboardMarkup:
    # Create inline buttons
    button1 = InlineKeyboardButton(text='English', callback_data='english')
    button2 = InlineKeyboardButton(text="O'zbek", callback_data='uzbek')
    button3 = InlineKeyboardButton(text='Русский', callback_data='russian')
    
    # Create a keyboard with the buttons
    keyboard = InlineKeyboardMarkup(row_width=2,inline_keyboard=[[button1,button2,button3]])
    
    return keyboard