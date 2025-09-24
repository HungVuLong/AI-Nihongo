"""Japanese text processing service."""

from typing import Dict, List, Any, Optional
import re

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from ..core.config import settings


class JapaneseProcessor:
    """Service for processing Japanese text."""
    
    def __init__(self):
        self.tokenizer = None
        self.is_initialized = False
        self.tokenizer_type = settings.tokenizer_model
    
    async def initialize(self) -> None:
        """Initialize Japanese processing tools."""
        if self.is_initialized:
            return
            
        logger.info("Initializing Japanese processor...")
        
        try:
            if self.tokenizer_type == "mecab":
                await self._initialize_mecab()
            elif self.tokenizer_type == "sudachi":
                await self._initialize_sudachi()
            else:
                logger.warning(f"Unknown tokenizer: {self.tokenizer_type}, using fallback")
                await self._initialize_fallback()
            
            self.is_initialized = True
            logger.info("Japanese processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Japanese processor: {e}")
            # Use fallback tokenizer
            await self._initialize_fallback()
            self.is_initialized = True
    
    async def _initialize_mecab(self) -> None:
        """Initialize MeCab tokenizer."""
        try:
            import fugashi
            import unidic_lite
            self.tokenizer = fugashi.Tagger()
            logger.info("MeCab tokenizer initialized")
        except ImportError:
            logger.warning("MeCab dependencies not found, using fallback")
            raise
    
    async def _initialize_sudachi(self) -> None:
        """Initialize SudachiPy tokenizer."""
        try:
            from sudachipy import tokenizer
            from sudachipy import dictionary
            
            dict_type = getattr(dictionary.DictionaryKind, 
                              settings.sudachi_dict_type.upper(), 
                              dictionary.DictionaryKind.CORE)
            
            self.tokenizer = dictionary.Dictionary(dict_type).create()
            logger.info("SudachiPy tokenizer initialized")
        except ImportError:
            logger.warning("SudachiPy not found, using fallback")
            raise
    
    async def _initialize_fallback(self) -> None:
        """Initialize fallback tokenizer."""
        logger.info("Using fallback Japanese processor")
        self.tokenizer = None
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze Japanese text and return detailed information.
        
        Args:
            text: Japanese text to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.is_initialized:
            await self.initialize()
        
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        if not cleaned_text:
            return self._empty_analysis(text)
        
        # Check if text contains Japanese characters
        if not self._contains_japanese(cleaned_text):
            return self._non_japanese_analysis(text)
        
        try:
            if self.tokenizer_type == "mecab" and self.tokenizer:
                return await self._analyze_with_mecab(cleaned_text)
            elif self.tokenizer_type == "sudachi" and self.tokenizer:
                return await self._analyze_with_sudachi(cleaned_text)
            else:
                return await self._analyze_fallback(cleaned_text)
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return await self._analyze_fallback(cleaned_text)
    
    async def _analyze_with_mecab(self, text: str) -> Dict[str, Any]:
        """Analyze text using MeCab."""
        tokens = []
        pos_tags = []
        pronunciations = []
        meanings = []
        
        for word in self.tokenizer(text):
            try:
                # Handle different MeCab feature formats
                if hasattr(word, 'feature'):
                    if hasattr(word.feature, 'split'):
                        # Older format where feature is a string
                        features = word.feature.split(',')
                    else:
                        # Newer format where feature is an object
                        features = [
                            getattr(word.feature, 'pos1', 'Unknown'),
                            getattr(word.feature, 'pos2', ''),
                            getattr(word.feature, 'pos3', ''),
                            getattr(word.feature, 'pos4', ''),
                            getattr(word.feature, 'ctype', ''),
                            getattr(word.feature, 'cform', ''),
                            getattr(word.feature, 'lemma', word.surface),
                            getattr(word.feature, 'kana', ''),
                            getattr(word.feature, 'pron', '')
                        ]
                else:
                    features = ['Unknown'] * 9
                
                token_info = {
                    "surface": word.surface,
                    "pos": features[0] if len(features) > 0 else "Unknown",
                    "pos_detail": features[1] if len(features) > 1 else "",
                    "base_form": features[6] if len(features) > 6 and features[6] != '*' else word.surface,
                    "reading": features[7] if len(features) > 7 and features[7] != '*' else "",
                    "pronunciation": features[8] if len(features) > 8 and features[8] != '*' else ""
                }
                
                tokens.append(token_info)
                pos_tags.append(token_info["pos"])
                
                if token_info["pronunciation"]:
                    pronunciations.append(token_info["pronunciation"])
                elif token_info["reading"]:
                    pronunciations.append(token_info["reading"])
                else:
                    pronunciations.append(token_info["surface"])
                    
            except Exception as e:
                logger.warning(f"Error processing token '{word.surface}': {e}")
                # Fallback token info
                token_info = {
                    "surface": word.surface,
                    "pos": "Unknown",
                    "pos_detail": "",
                    "base_form": word.surface,
                    "reading": "",
                    "pronunciation": ""
                }
                tokens.append(token_info)
                pos_tags.append("Unknown")
                pronunciations.append(word.surface)
        
        return {
            "original_text": text,
            "tokens": tokens,
            "pos_tags": pos_tags,
            "pronunciations": pronunciations,
            "meanings": meanings,
            "difficulty_level": self._estimate_difficulty(tokens),
            "kanji_info": self._extract_kanji_info(text),
            "grammar_patterns": self._identify_grammar_patterns(tokens)
        }
    
    async def _analyze_with_sudachi(self, text: str) -> Dict[str, Any]:
        """Analyze text using SudachiPy."""
        tokens = []
        pos_tags = []
        pronunciations = []
        
        morphemes = self.tokenizer.tokenize(text)
        
        for m in morphemes:
            token_info = {
                "surface": m.surface(),
                "pos": m.part_of_speech()[0],
                "pos_detail": m.part_of_speech()[1],
                "base_form": m.dictionary_form(),
                "reading": m.reading_form(),
                "pronunciation": m.pronunciation_form()
            }
            
            tokens.append(token_info)
            pos_tags.append(token_info["pos"])
            pronunciations.append(token_info["pronunciation"] or token_info["reading"] or token_info["surface"])
        
        return {
            "original_text": text,
            "tokens": tokens,
            "pos_tags": pos_tags,
            "pronunciations": pronunciations,
            "meanings": [],
            "difficulty_level": self._estimate_difficulty(tokens),
            "kanji_info": self._extract_kanji_info(text),
            "grammar_patterns": self._identify_grammar_patterns(tokens)
        }
    
    async def _analyze_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback analysis without external libraries."""
        # Simple character-based analysis
        tokens = []
        for char in text:
            if char.strip():  # Skip whitespace
                token_info = {
                    "surface": char,
                    "pos": self._guess_pos(char),
                    "pos_detail": "",
                    "base_form": char,
                    "reading": "",
                    "pronunciation": ""
                }
                tokens.append(token_info)
        
        return {
            "original_text": text,
            "tokens": tokens,
            "pos_tags": [t["pos"] for t in tokens],
            "pronunciations": [t["surface"] for t in tokens],
            "meanings": [],
            "difficulty_level": self._estimate_difficulty_simple(text),
            "kanji_info": self._extract_kanji_info(text),
            "grammar_patterns": []
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize Japanese text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize full-width characters
        text = text.replace('　', ' ')  # Full-width space to regular space
        
        return text
    
    def _contains_japanese(self, text: str) -> bool:
        """Check if text contains Japanese characters."""
        japanese_ranges = [
            (0x3040, 0x309F),  # Hiragana
            (0x30A0, 0x30FF),  # Katakana
            (0x4E00, 0x9FAF),  # CJK Unified Ideographs (Kanji)
            (0x3400, 0x4DBF),  # CJK Extension A
        ]
        
        for char in text:
            char_code = ord(char)
            for start, end in japanese_ranges:
                if start <= char_code <= end:
                    return True
        return False
    
    def _guess_pos(self, char: str) -> str:
        """Guess part of speech for a character (fallback method)."""
        char_code = ord(char)
        
        if 0x3040 <= char_code <= 0x309F:  # Hiragana
            return "助詞"  # Particle (common for hiragana)
        elif 0x30A0 <= char_code <= 0x30FF:  # Katakana
            return "名詞"  # Noun (common for katakana)
        elif 0x4E00 <= char_code <= 0x9FAF:  # Kanji
            return "名詞"  # Noun (common for kanji)
        else:
            return "記号"  # Symbol
    
    def _extract_kanji_info(self, text: str) -> List[Dict[str, Any]]:
        """Extract information about kanji characters."""
        kanji_info = []
        
        for char in text:
            char_code = ord(char)
            if 0x4E00 <= char_code <= 0x9FAF:  # Kanji range
                kanji_info.append({
                    "character": char,
                    "unicode": hex(char_code),
                    "stroke_count": None,  # Would need external data
                    "grade": None,  # Would need external data
                    "frequency": None  # Would need external data
                })
        
        return kanji_info
    
    def _identify_grammar_patterns(self, tokens: List[Dict[str, Any]]) -> List[str]:
        """Identify common Japanese grammar patterns."""
        patterns = []
        
        # Simple pattern detection
        pos_sequence = [token["pos"] for token in tokens]
        
        # Common patterns
        if "動詞" in pos_sequence and "助詞" in pos_sequence:
            patterns.append("verb_particle_construction")
        
        if "形容詞" in pos_sequence:
            patterns.append("adjective_usage")
        
        return patterns
    
    def _estimate_difficulty(self, tokens: List[Dict[str, Any]]) -> str:
        """Estimate difficulty level based on tokens."""
        if not tokens:
            return "unknown"
        
        # Simple heuristic based on token count and kanji presence
        kanji_count = sum(1 for token in tokens if self._contains_kanji(token["surface"]))
        total_tokens = len(tokens)
        
        kanji_ratio = kanji_count / total_tokens if total_tokens > 0 else 0
        
        if kanji_ratio > 0.5:
            return "advanced"
        elif kanji_ratio > 0.2:
            return "intermediate"
        else:
            return "beginner"
    
    def _estimate_difficulty_simple(self, text: str) -> str:
        """Simple difficulty estimation for fallback."""
        kanji_count = sum(1 for char in text if self._contains_kanji(char))
        total_chars = len([char for char in text if char.strip()])
        
        if total_chars == 0:
            return "unknown"
        
        kanji_ratio = kanji_count / total_chars
        
        if kanji_ratio > 0.4:
            return "advanced"
        elif kanji_ratio > 0.1:
            return "intermediate"
        else:
            return "beginner"
    
    def _contains_kanji(self, text: str) -> bool:
        """Check if text contains kanji characters."""
        for char in text:
            char_code = ord(char)
            if 0x4E00 <= char_code <= 0x9FAF:
                return True
        return False
    
    def _empty_analysis(self, text: str) -> Dict[str, Any]:
        """Return empty analysis for invalid input."""
        return {
            "original_text": text,
            "tokens": [],
            "pos_tags": [],
            "pronunciations": [],
            "meanings": [],
            "difficulty_level": "unknown",
            "kanji_info": [],
            "grammar_patterns": []
        }
    
    def _non_japanese_analysis(self, text: str) -> Dict[str, Any]:
        """Return analysis for non-Japanese text."""
        return {
            "original_text": text,
            "tokens": [{"surface": text, "pos": "foreign", "pos_detail": "", "base_form": text, "reading": "", "pronunciation": ""}],
            "pos_tags": ["foreign"],
            "pronunciations": [text],
            "meanings": [],
            "difficulty_level": "not_japanese",
            "kanji_info": [],
            "grammar_patterns": []
        }