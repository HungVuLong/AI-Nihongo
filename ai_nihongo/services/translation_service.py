"""Translation service with multiple providers for accurate translations."""

from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from enum import Enum
import asyncio

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class TranslationProvider(Enum):
    """Supported translation providers."""
    GOOGLE = "google"
    DEEPL = "deepl"
    MICROSOFT = "microsoft"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    SIMPLE = "simple"


class LanguageCode:
    """Common language codes for translation."""
    ENGLISH = "en"
    JAPANESE = "ja"
    CHINESE = "zh"
    KOREAN = "ko"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"


class BaseTranslationProvider(ABC):
    """Base class for translation providers."""
    
    @abstractmethod
    async def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate text from source to target language."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the translation provider."""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        pass


class SimpleTranslationProvider(BaseTranslationProvider):
    """Simple rule-based translation provider for common phrases."""
    
    def __init__(self):
        self.is_initialized = False
        self.translations = {
            # Japanese to English
            ("ja", "en"): {
                "こんにちは": "Hello",
                "こんばんは": "Good evening",
                "おはよう": "Good morning",
                "おはようございます": "Good morning (polite)",
                "ありがとう": "Thank you",
                "ありがとうございます": "Thank you very much",
                "すみません": "Excuse me / I'm sorry",
                "はい": "Yes",
                "いいえ": "No",
                "さようなら": "Goodbye",
                "また明日": "See you tomorrow",
                "お疲れ様": "Good work / Thank you for your hard work",
                "私": "I / me",
                "あなた": "You",
                "彼": "He",
                "彼女": "She",
                "学生": "student",
                "先生": "teacher",
                "友達": "friend",
                "家族": "family",
                "食べる": "to eat",
                "飲む": "to drink",
                "行く": "to go",
                "来る": "to come",
                "見る": "to see/watch",
                "読む": "to read",
                "書く": "to write",
                "話す": "to speak",
                "聞く": "to listen/hear",
                "わかる": "to understand",
                "好き": "like",
                "嫌い": "dislike",
                "大きい": "big",
                "小さい": "small",
                "新しい": "new",
                "古い": "old",
                "美しい": "beautiful",
                "今日": "today",
                "昨日": "yesterday",
                "明日": "tomorrow",
                "朝": "morning",
                "昼": "noon/lunch",
                "夜": "night",
                "時間": "time",
                "お金": "money",
                "仕事": "work/job",
                "学校": "school",
                "家": "house/home",
                "駅": "station",
                "病院": "hospital",
                "レストラン": "restaurant",
                "コンビニ": "convenience store",
                "映画": "movie",
                "音楽": "music",
                "本": "book",
                "車": "car",
                "電車": "train",
                "バス": "bus",
                "飛行機": "airplane"
            },
            # English to Japanese
            ("en", "ja"): {
                "hello": "こんにちは",
                "good morning": "おはようございます",
                "good evening": "こんばんは",
                "thank you": "ありがとうございます",
                "excuse me": "すみません",
                "sorry": "すみません",
                "yes": "はい",
                "no": "いいえ",
                "goodbye": "さようなら",
                "see you tomorrow": "また明日",
                "i": "私",
                "you": "あなた",
                "he": "彼",
                "she": "彼女",
                "student": "学生",
                "teacher": "先生",
                "friend": "友達",
                "family": "家族",
                "eat": "食べる",
                "drink": "飲む",
                "go": "行く",
                "come": "来る",
                "see": "見る",
                "watch": "見る",
                "read": "読む",
                "write": "書く",
                "speak": "話す",
                "listen": "聞く",
                "understand": "わかる",
                "like": "好き",
                "dislike": "嫌い",
                "big": "大きい",
                "small": "小さい",
                "new": "新しい",
                "old": "古い",
                "beautiful": "美しい",
                "today": "今日",
                "yesterday": "昨日",
                "tomorrow": "明日",
                "morning": "朝",
                "noon": "昼",
                "night": "夜",
                "time": "時間",
                "money": "お金",
                "work": "仕事",
                "job": "仕事",
                "school": "学校",
                "house": "家",
                "home": "家",
                "station": "駅",
                "hospital": "病院",
                "restaurant": "レストラン",
                "movie": "映画",
                "music": "音楽",
                "book": "本",
                "car": "車",
                "train": "電車",
                "bus": "バス",
                "airplane": "飛行機"
            }
        }
    
    async def initialize(self) -> None:
        """Initialize simple translation provider."""
        self.is_initialized = True
        logger.info("Simple translation provider initialized")
    
    async def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate using simple dictionary lookup."""
        if not self.is_initialized:
            await self.initialize()
        
        translation_dict = self.translations.get((source_lang, target_lang), {})
        
        # Try exact match first (preserve original case for Japanese)
        original_text = text.strip()
        text_lower = text.lower().strip()
        
        # For Japanese text, try both original and lowercase
        if source_lang == "ja" or target_lang == "ja":
            if original_text in translation_dict:
                return {
                    "translated_text": translation_dict[original_text],
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "confidence": 0.9,
                    "provider": "simple",
                    "method": "exact_match"
                }
        
        # Try lowercase for English
        if text_lower in translation_dict:
            return {
                "translated_text": translation_dict[text_lower],
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": 0.9,
                "provider": "simple",
                "method": "exact_match"
            }
        
        # Try word-by-word translation for longer text
        words = text_lower.split()
        if len(words) > 1:
            translated_words = []
            found_any = False
            
            for word in words:
                if word in translation_dict:
                    translated_words.append(translation_dict[word])
                    found_any = True
                else:
                    translated_words.append(f"[{word}]")  # Mark untranslated words
            
            if found_any:
                return {
                    "translated_text": " ".join(translated_words),
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "confidence": 0.6,
                    "provider": "simple",
                    "method": "word_by_word",
                    "note": "Some words marked with [] could not be translated"
                }
        
        # No translation found
        return {
            "translated_text": f"[Translation not available for '{text}']",
            "source_language": source_lang,
            "target_language": target_lang,
            "confidence": 0.0,
            "provider": "simple",
            "method": "not_found",
            "note": "Consider using a more advanced translation provider for better results"
        }
    
    def get_supported_languages(self) -> List[str]:
        """Get supported language codes."""
        return ["ja", "en"]


class GoogleTranslateProvider(BaseTranslationProvider):
    """Google Translate provider using googletrans library."""
    
    def __init__(self):
        self.translator = None
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize Google Translate provider."""
        try:
            # Try to import googletrans
            from googletrans import Translator
            self.translator = Translator()
            self.is_initialized = True
            logger.info("Google Translate provider initialized")
        except ImportError:
            logger.warning("googletrans not installed. Run: pip install googletrans==4.0.0-rc1")
            raise Exception("googletrans package not available")
        except Exception as e:
            logger.error(f"Failed to initialize Google Translate: {e}")
            raise
    
    async def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate using Google Translate."""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Perform translation
            result = self.translator.translate(text, src=source_lang, dest=target_lang)
            
            return {
                "translated_text": result.text,
                "source_language": result.src,
                "target_language": target_lang,
                "confidence": 0.9,  # Google Translate is generally reliable
                "provider": "google",
                "method": "api",
                "detected_language": result.src if source_lang == "auto" else source_lang
            }
        except Exception as e:
            logger.error(f"Google Translate error: {e}")
            raise
    
    def get_supported_languages(self) -> List[str]:
        """Get supported language codes."""
        # Google Translate supports many languages
        return ["auto", "ja", "en", "zh", "ko", "es", "fr", "de", "it", "pt", "ru", "ar", "hi", "th", "vi"]


class LLMTranslationProvider(BaseTranslationProvider):
    """Translation provider using LLM services."""
    
    def __init__(self, llm_provider: str = "anthropic"):
        self.llm_provider = llm_provider
        self.llm_service = None
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize LLM translation provider."""
        try:
            from .llm_service import LLMService
            self.llm_service = LLMService()
            await self.llm_service.initialize(provider=self.llm_provider)
            self.is_initialized = True
            logger.info(f"LLM translation provider initialized with {self.llm_provider}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM translation provider: {e}")
            raise
    
    async def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate using LLM."""
        if not self.is_initialized:
            await self.initialize()
        
        # Language code to name mapping
        lang_names = {
            "ja": "Japanese",
            "en": "English",
            "zh": "Chinese",
            "ko": "Korean",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian"
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        # Construct translation prompt
        prompt = f"""Please translate the following text from {source_name} to {target_name}.
Provide only the translation, no explanations or additional text.

Text to translate: {text}

Translation:"""
        
        # Add context if available
        if context and context.get("japanese_analysis"):
            analysis = context["japanese_analysis"]
            prompt = f"""Please translate the following {source_name} text to {target_name}.
The text has been analyzed and contains the following linguistic information: {analysis}
Provide only the translation, no explanations or additional text.

Text to translate: {text}

Translation:"""
        
        try:
            translation = await self.llm_service.generate_response(prompt)
            
            return {
                "translated_text": translation.strip(),
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": 0.85,  # LLM translations are generally good
                "provider": f"llm_{self.llm_provider}",
                "method": "llm_generation",
                "model": self.llm_provider
            }
        except Exception as e:
            logger.error(f"LLM translation error: {e}")
            raise
    
    def get_supported_languages(self) -> List[str]:
        """Get supported language codes."""
        return ["ja", "en", "zh", "ko", "es", "fr", "de", "it", "pt", "ru"]


class TranslationService:
    """Main translation service that manages multiple providers."""
    
    def __init__(self):
        self.providers: Dict[TranslationProvider, BaseTranslationProvider] = {}
        self.default_provider = TranslationProvider.SIMPLE
        self.is_initialized = False
        
        # Provider preferences by language pair
        self.provider_preferences = {
            ("ja", "en"): [TranslationProvider.GOOGLE, TranslationProvider.ANTHROPIC, TranslationProvider.SIMPLE],
            ("en", "ja"): [TranslationProvider.GOOGLE, TranslationProvider.ANTHROPIC, TranslationProvider.SIMPLE],
            ("auto", "en"): [TranslationProvider.GOOGLE, TranslationProvider.ANTHROPIC, TranslationProvider.SIMPLE],
            ("auto", "ja"): [TranslationProvider.GOOGLE, TranslationProvider.ANTHROPIC, TranslationProvider.SIMPLE],
        }
    
    async def initialize(self) -> None:
        """Initialize all available translation providers."""
        if self.is_initialized:
            return
        
        logger.info("Initializing translation service...")
        
        # Initialize simple provider (always available)
        simple_provider = SimpleTranslationProvider()
        await simple_provider.initialize()
        self.providers[TranslationProvider.SIMPLE] = simple_provider
        
        # Try to initialize Google Translate
        try:
            google_provider = GoogleTranslateProvider()
            await google_provider.initialize()
            self.providers[TranslationProvider.GOOGLE] = google_provider
            logger.info("Google Translate provider added")
        except Exception as e:
            logger.warning(f"Google Translate provider not available: {e}")
        
        # Try to initialize Anthropic LLM provider
        try:
            anthropic_provider = LLMTranslationProvider("anthropic")
            await anthropic_provider.initialize()
            self.providers[TranslationProvider.ANTHROPIC] = anthropic_provider
            logger.info("Anthropic translation provider added")
        except Exception as e:
            logger.warning(f"Anthropic translation provider not available: {e}")
        
        # Try to initialize Ollama LLM provider
        try:
            ollama_provider = LLMTranslationProvider("ollama")
            await ollama_provider.initialize()
            self.providers[TranslationProvider.OLLAMA] = ollama_provider
            logger.info("Ollama translation provider added")
        except Exception as e:
            logger.warning(f"Ollama translation provider not available: {e}")
        
        self.is_initialized = True
        logger.info(f"Translation service initialized with {len(self.providers)} providers")
    
    async def translate(
        self, 
        text: str, 
        target_lang: str = "en",
        source_lang: str = "auto",
        provider: Optional[TranslationProvider] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate text using the best available provider."""
        if not self.is_initialized:
            await self.initialize()
        
        # Detect source language if auto
        actual_source_lang = source_lang
        if source_lang == "auto":
            actual_source_lang = await self.detect_language(text)
            logger.info(f"Detected language: {actual_source_lang} for text: {text[:50]}...")
        
        # If specific provider requested
        if provider and provider in self.providers:
            try:
                return await self.providers[provider].translate(text, actual_source_lang, target_lang, context)
            except Exception as e:
                logger.warning(f"Requested provider {provider.value} failed: {e}")
                # Fall through to automatic provider selection
        
        # Get preferred providers for this language pair
        lang_pair = (actual_source_lang, target_lang)
        preferred_providers = self.provider_preferences.get(lang_pair, [TranslationProvider.SIMPLE])
        
        # Try providers in order of preference
        for pref_provider in preferred_providers:
            if pref_provider in self.providers:
                try:
                    result = await self.providers[pref_provider].translate(text, actual_source_lang, target_lang, context)
                    logger.info(f"Translation successful with {pref_provider.value} provider")
                    return result
                except Exception as e:
                    logger.warning(f"Provider {pref_provider.value} failed: {e}")
                    continue
        
        # If all providers failed, return error
        return {
            "translated_text": f"[Translation failed for '{text}']",
            "source_language": actual_source_lang,
            "target_language": target_lang,
            "confidence": 0.0,
            "provider": "none",
            "method": "error",
            "error": "All translation providers failed"
        }
    
    async def detect_language(self, text: str) -> str:
        """Detect the language of the text."""
        # Simple heuristic language detection
        japanese_chars = set('あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん')
        japanese_chars.update('アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン')
        japanese_chars.update('がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ')
        japanese_chars.update('ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ')
        
        # Count Japanese characters
        japanese_count = sum(1 for char in text if char in japanese_chars)
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return "unknown"
        
        japanese_ratio = japanese_count / total_chars
        
        if japanese_ratio > 0.3:  # If more than 30% are Japanese characters
            return "ja"
        else:
            return "en"  # Default to English for non-Japanese text
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [provider.value for provider in self.providers.keys()]
    
    def get_supported_languages(self) -> Dict[str, List[str]]:
        """Get supported languages for each provider."""
        result = {}
        for provider_enum, provider_instance in self.providers.items():
            result[provider_enum.value] = provider_instance.get_supported_languages()
        return result