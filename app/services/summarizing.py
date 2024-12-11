from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable, NoTranscriptFound
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.tokenizers import Tokenizer

from app.services.translations import get_translations
from app.configs import logger

async def get_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    if "youtube.com" in url or "youtu.be" in url:
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        else:
            return url.split("/")[-1]
    return None


async def fetch_subtitles(video_id: str, languages: list, user_lang:str) -> str:
    """Fetch subtitles for a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        subtitles = "\n".join([f"{item['text']}" for item in transcript])
        logger.debug(subtitles)
        return subtitles
    except TranscriptsDisabled as e:
        logger.debug(e)
        return get_translations(user_lang,'subtitles_disabled')
    except VideoUnavailable as e:
        logger.debug(e)
        return get_translations(user_lang, 'video_unavailable') 
    except NoTranscriptFound as e:
        logger.debug(e)
        return get_translations(user_lang, 'no_transcript_found') 
    except Exception as e:
        logger.debug(e)
        return get_translations(user_lang, 'error_occurred')

async def summarize_text(text: str, num_sentences: int = 3, max_length: int = None) -> str:
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