import telebot
from googletrans import Translator  # For Google Translate API
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable, NoTranscriptFound
import os
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.tokenizers import Tokenizer
import re

# Your bot's token from BotFather
BOT_TOKEN = "7630519726:AAHjydMNpG1xfcu810ayavUv2KIZ6YH83WM"
bot = telebot.TeleBot(BOT_TOKEN)

# Path to save the subtitles file
SUBTITLE_FOLDER = "uploads"

# Create a Translator instance (Google Translate API)
translator = Translator()

# Language dictionaries for messages
messages = {
    'en': {
        'start': "Welcome! Send me a YouTube video URL, and I'll fetch the subtitles for you.",
        'invalid_url': "Invalid YouTube URL. Please try again.",
        'fetching_subtitles': "Fetching subtitles...",
        'subtitles_disabled': "Subtitles are disabled for this video.",
        'video_unavailable': "The video is unavailable or private.",
        'no_transcript_found': "No subtitles found for the requested language.",
        'error_occurred': "An error occurred: {}",
        'summary_generated': "Summary generated:",
        'summary_too_large': "The summary is too large. Sending in chunks:",
        'subtitles_saved': "Subtitles summary saved and sent as a file."
    },
    'ru': {
        'start': "Добро пожаловать! Отправьте мне ссылку на видео YouTube, и я получу для вас субтитры.",
        'invalid_url': "Неверный URL YouTube. Пожалуйста, попробуйте снова.",
        'fetching_subtitles': "Получение субтитров...",
        'subtitles_disabled': "Субтитры отключены для этого видео.",
        'video_unavailable': "Видео недоступно или приватное.",
        'no_transcript_found': "Субтитры для выбранного языка не найдены.",
        'error_occurred': "Произошла ошибка: {}",
        'summary_generated': "Резюме сгенерировано:",
        'summary_too_large': "Резюме слишком большое. Отправляю по частям:",
        'subtitles_saved': "Резюме субтитров сохранено и отправлено в виде файла."
    },
    'uz': {
        'start': "Xush kelibsiz! Menga YouTube video URL yuboring, va men siz uchun subtitrlarni olishni boshlayman.",
        'invalid_url': "Noto'g'ri YouTube URL. Iltimos, qayta urinib ko'ring.",
        'fetching_subtitles': "Subtitrlarni olish...",
        'subtitles_disabled': "Bu videoda subtitrlar o'chirilgan.",
        'video_unavailable': "Video mavjud emas yoki maxfiy.",
        'no_transcript_found': "So'ralgan tilga oid subtitrlar topilmadi.",
        'error_occurred': "Xato yuz berdi: {}",
        'summary_generated': "Xulosa yaratildi:",
        'summary_too_large': "Xulosa juda katta. Qismlarga bo'lib yuborilmoqda:",
        'subtitles_saved': "Subtitr xulosasi saqlandi va fayl sifatida yuborildi."
    }
}

# Function to send a message in the selected language
def send_message_in_language(chat_id, message_key, lang='en', *args):
    """Send the message in the selected language."""
    if lang in messages:
        message = messages[lang].get(message_key, "Message not found.")
        bot.send_message(chat_id, message.format(*args))

def get_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    if "youtube.com" in url or "youtu.be" in url:
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        else:
            return url.split("/")[-1]
    return None

def fetch_subtitles(video_id: str, languages: list) -> str:
    """Fetch subtitles for a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        subtitles = "\n".join([f"{item['text']}" for item in transcript])
        return subtitles
    except TranscriptsDisabled:
        return messages['en']['subtitles_disabled']
    except VideoUnavailable:
        return messages['en']['video_unavailable']
    except NoTranscriptFound:
        return messages['en']['no_transcript_found']
    except Exception as e:
        return messages['en']['error_occurred'].format(str(e))

def summarize_text(text: str, num_sentences: int = 3, max_length: int = None) -> str:
    """Summarize the input text to a specified number of sentences, with an optional max length."""
    if not text.strip():
        return "Error: Input text is empty or invalid."
    
    try:
        # Initialize tokenizer and parser
        tokenizer = Tokenizer(language="en")
        parser = PlaintextParser.from_string(text, tokenizer)
        
        # Initialize LSA summarizer
        summarizer = LsaSummarizer()
        
        # Generate the summary
        summary = summarizer(parser.document, num_sentences)
        
        # Combine the summary sentences
        summary_text = " ".join(str(sentence) for sentence in summary)
        
        # Apply max length constraint
        if max_length and len(summary_text) > max_length:
            summary_text = summary_text[:max_length].rsplit(" ", 1)[0] + "..."
        
        return summary_text or "Could not generate summary. Try with more text."
    except Exception as e:
        return f"Error while summarizing: {str(e)}"

def translate_text(text: str, target_language: str) -> str:
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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handle the /start command."""
    user_lang = 'en'  # Default language
    send_message_in_language(message.chat.id, 'start', user_lang)

@bot.message_handler(func=lambda message: True)
def handle_youtube_url(message):
    """Handle YouTube URLs."""
    url = message.text
    video_id = get_video_id(url)

    if not video_id:
        send_message_in_language(message.chat.id, 'invalid_url', 'en')
        return

    send_message_in_language(message.chat.id, 'fetching_subtitles', 'en')
    subtitles = fetch_subtitles(video_id, languages=['en', 'ru', 'uz'])

    if subtitles:
        # Summarize the subtitles
        summary = summarize_text(subtitles, max_length=300)

        # Translate the summary if needed (for example, to Russian or Uzbek)
        user_lang = 'ru'  # Change this based on user's preference
        translated_summary = translate_text(summary, user_lang)

        # Send the translated summary
        send_message_in_language(message.chat.id, 'summary_generated', user_lang)
        bot.send_message(message.chat.id, translated_summary)
        
        # Optionally, save the summarized subtitles to a file
        if not os.path.exists(SUBTITLE_FOLDER):
            os.makedirs(SUBTITLE_FOLDER)

        file_name = f"{video_id}_subtitles_summary.txt"
        file_name = re.sub(r'[\\/*?:"<>|]', "_", file_name)
        file_path = os.path.join(SUBTITLE_FOLDER, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(translated_summary)

        with open(file_path, "rb") as file_to_send:
            bot.send_document(message.chat.id, file_to_send)

        os.remove(file_path)  # Clean up the file after sending

if __name__ == "__main__":
    print("Bot is running...")
    bot.polling()
