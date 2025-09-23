"""
Utility functions for AI-Nihongo application.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import re


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('ai_nihongo.log')
        ]
    )
    return logging.getLogger(__name__)


def validate_japanese_text(text: str) -> bool:
    """Validate if text contains Japanese characters."""
    # Japanese character ranges
    hiragana = re.compile(r'[\u3040-\u309F]')
    katakana = re.compile(r'[\u30A0-\u30FF]')
    kanji = re.compile(r'[\u4E00-\u9FAF]')
    
    return bool(hiragana.search(text) or katakana.search(text) or kanji.search(text))


def clean_text(text: str) -> str:
    """Clean and normalize text input."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF.,!?]', '', text)
    
    return text


def save_progress(user_id: str, progress_data: Dict[str, Any]) -> bool:
    """Save user progress to file."""
    try:
        progress_dir = Path("data/progress")
        progress_dir.mkdir(parents=True, exist_ok=True)
        
        progress_file = progress_dir / f"{user_id}_progress.json"
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        logging.error(f"Failed to save progress: {str(e)}")
        return False


def load_progress(user_id: str) -> Optional[Dict[str, Any]]:
    """Load user progress from file."""
    try:
        progress_file = Path("data/progress") / f"{user_id}_progress.json"
        
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    except Exception as e:
        logging.error(f"Failed to load progress: {str(e)}")
        return None


def format_japanese_text(text: str, include_furigana: bool = False) -> str:
    """Format Japanese text for display."""
    if not text:
        return ""
    
    # Basic formatting - can be enhanced with furigana support
    formatted = text.strip()
    
    # Add spacing around punctuation
    formatted = re.sub(r'([。、！？])', r'\1 ', formatted)
    
    return formatted.strip()


def calculate_difficulty_score(text: str) -> str:
    """Calculate difficulty level of Japanese text."""
    if not text or not validate_japanese_text(text):
        return "unknown"
    
    # Simple heuristic based on character types
    hiragana_count = len(re.findall(r'[\u3040-\u309F]', text))
    katakana_count = len(re.findall(r'[\u30A0-\u30FF]', text))
    kanji_count = len(re.findall(r'[\u4E00-\u9FAF]', text))
    
    total_chars = hiragana_count + katakana_count + kanji_count
    
    if total_chars == 0:
        return "unknown"
    
    kanji_ratio = kanji_count / total_chars
    
    if kanji_ratio < 0.2:
        return "beginner"
    elif kanji_ratio < 0.4:
        return "intermediate"
    else:
        return "advanced"


def romanize_japanese(text: str) -> str:
    """Basic romanization of Japanese text (simplified)."""
    # This is a basic implementation - a full romanization would require
    # libraries like pykakasi or mecab
    
    hiragana_to_romaji = {
        'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
        'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
        'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
        'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
        'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
        'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
        'だ': 'da', 'ぢ': 'ji', 'づ': 'zu', 'で': 'de', 'ど': 'do',
        'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
        'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
        'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
        'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
        'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
        'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
        'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
        'わ': 'wa', 'を': 'wo', 'ん': 'n'
    }
    
    result = ""
    for char in text:
        if char in hiragana_to_romaji:
            result += hiragana_to_romaji[char]
        else:
            result += char
    
    return result


def get_study_stats(progress_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate study statistics from progress data."""
    if not progress_data:
        return {
            "total_sessions": 0,
            "total_words_studied": 0,
            "average_score": 0,
            "streak_days": 0,
            "favorite_topics": []
        }
    
    sessions = progress_data.get("sessions", [])
    
    stats = {
        "total_sessions": len(sessions),
        "total_words_studied": sum(session.get("words_count", 0) for session in sessions),
        "average_score": 0,
        "streak_days": progress_data.get("streak_days", 0),
        "favorite_topics": []
    }
    
    if sessions:
        scores = [session.get("score", 0) for session in sessions if session.get("score")]
        if scores:
            stats["average_score"] = sum(scores) / len(scores)
        
        # Find most common topics
        topics = [session.get("topic") for session in sessions if session.get("topic")]
        topic_counts = {}
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        stats["favorite_topics"] = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return stats


def create_sample_data():
    """Create sample data files for testing."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Sample vocabulary data
    sample_vocab = {
        "daily_life": [
            {"japanese": "おはよう", "hiragana": "おはよう", "english": "Good morning", "vietnamese": "Chào buổi sáng"},
            {"japanese": "こんにちは", "hiragana": "こんにちは", "english": "Hello", "vietnamese": "Xin chào"},
            {"japanese": "ありがとう", "hiragana": "ありがとう", "english": "Thank you", "vietnamese": "Cảm ơn"}
        ]
    }
    
    vocab_file = data_dir / "sample_vocabulary.json"
    with open(vocab_file, 'w', encoding='utf-8') as f:
        json.dump(sample_vocab, f, ensure_ascii=False, indent=2)
    
    return str(vocab_file)