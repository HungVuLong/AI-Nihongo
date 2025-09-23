"""
Vocabulary practice module for Japanese learning.
"""

from typing import List, Dict, Any, Optional
import random
from ..llm.client import llm_client
from ..core.config import config


class VocabularyPractice:
    """Vocabulary practice exercises for Japanese learning."""
    
    def __init__(self):
        """Initialize vocabulary practice."""
        self.difficulty_levels = ["beginner", "intermediate", "advanced"]
        self.topics = [
            "daily_life", "food", "family", "work", "travel", "nature",
            "emotions", "colors", "numbers", "time", "weather", "shopping"
        ]
    
    def get_vocabulary_set(
        self,
        topic: str = "daily_life",
        difficulty: str = "beginner",
        count: int = 10,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Get a set of vocabulary words for practice."""
        try:
            questions = llm_client.generate_practice_questions(
                topic=f"vocabulary - {topic}",
                difficulty=difficulty,
                language=language,
                count=count
            )
            return questions
        except Exception as e:
            # Fallback vocabulary set
            return self._get_fallback_vocabulary(topic, count)
    
    def _get_fallback_vocabulary(self, topic: str, count: int) -> List[Dict[str, Any]]:
        """Fallback vocabulary set when LLM is unavailable."""
        basic_vocab = {
            "daily_life": [
                {"japanese": "おはよう", "hiragana": "おはよう", "english": "Good morning", "vietnamese": "Chào buổi sáng"},
                {"japanese": "こんにちは", "hiragana": "こんにちは", "english": "Hello", "vietnamese": "Xin chào"},
                {"japanese": "ありがとう", "hiragana": "ありがとう", "english": "Thank you", "vietnamese": "Cảm ơn"},
                {"japanese": "すみません", "hiragana": "すみません", "english": "Excuse me", "vietnamese": "Xin lỗi"},
                {"japanese": "さようなら", "hiragana": "さようなら", "english": "Goodbye", "vietnamese": "Tạm biệt"},
            ],
            "food": [
                {"japanese": "食べ物", "hiragana": "たべもの", "english": "Food", "vietnamese": "Thức ăn"},
                {"japanese": "水", "hiragana": "みず", "english": "Water", "vietnamese": "Nước"},
                {"japanese": "お茶", "hiragana": "おちゃ", "english": "Tea", "vietnamese": "Trà"},
                {"japanese": "ご飯", "hiragana": "ごはん", "english": "Rice/Meal", "vietnamese": "Cơm"},
                {"japanese": "魚", "hiragana": "さかな", "english": "Fish", "vietnamese": "Cá"},
            ],
            "family": [
                {"japanese": "家族", "hiragana": "かぞく", "english": "Family", "vietnamese": "Gia đình"},
                {"japanese": "お父さん", "hiragana": "おとうさん", "english": "Father", "vietnamese": "Bố"},
                {"japanese": "お母さん", "hiragana": "おかあさん", "english": "Mother", "vietnamese": "Mẹ"},
                {"japanese": "兄", "hiragana": "あに", "english": "Older brother", "vietnamese": "Anh trai"},
                {"japanese": "姉", "hiragana": "あね", "english": "Older sister", "vietnamese": "Chị gái"},
            ]
        }
        
        vocab_list = basic_vocab.get(topic, basic_vocab["daily_life"])
        selected_vocab = random.sample(vocab_list, min(count, len(vocab_list)))
        
        questions = []
        for vocab in selected_vocab:
            questions.append({
                "question": f"What does '{vocab['japanese']}' mean?",
                "type": "vocabulary",
                "japanese": vocab["japanese"],
                "hiragana": vocab["hiragana"],
                "correct_answer": vocab["english"],
                "vietnamese": vocab["vietnamese"],
                "explanation": f"{vocab['japanese']} ({vocab['hiragana']}) means '{vocab['english']}' in English and '{vocab['vietnamese']}' in Vietnamese."
            })
        
        return questions
    
    def practice_flashcards(
        self,
        vocabulary_set: List[Dict[str, Any]],
        language: str = "en"
    ) -> Dict[str, Any]:
        """Practice vocabulary using flashcard method."""
        if not vocabulary_set:
            return {"error": "No vocabulary set provided"}
        
        results = {
            "total_words": len(vocabulary_set),
            "words": vocabulary_set,
            "study_mode": "flashcards",
            "language": language
        }
        
        return results
    
    def quiz_vocabulary(
        self,
        vocabulary_set: List[Dict[str, Any]],
        quiz_type: str = "multiple_choice"
    ) -> List[Dict[str, Any]]:
        """Create vocabulary quiz questions."""
        quiz_questions = []
        
        for vocab in vocabulary_set:
            if quiz_type == "multiple_choice":
                # Create multiple choice question
                question = {
                    "question": f"What does '{vocab.get('japanese', vocab.get('question', ''))}' mean?",
                    "type": "multiple_choice",
                    "correct_answer": vocab.get("correct_answer", vocab.get("english", "")),
                    "explanation": vocab.get("explanation", "")
                }
                quiz_questions.append(question)
            
            elif quiz_type == "translation":
                question = {
                    "question": f"Translate to Japanese: {vocab.get('correct_answer', vocab.get('english', ''))}",
                    "type": "translation",
                    "correct_answer": vocab.get("japanese", ""),
                    "explanation": vocab.get("explanation", "")
                }
                quiz_questions.append(question)
        
        return quiz_questions


class GrammarPractice:
    """Grammar practice exercises for Japanese learning."""
    
    def __init__(self):
        """Initialize grammar practice."""
        self.grammar_points = [
            "particles", "verb_conjugation", "adjectives", "sentence_structure",
            "politeness_levels", "tenses", "conditionals", "passive_voice"
        ]
    
    def get_grammar_exercises(
        self,
        grammar_point: str = "particles",
        difficulty: str = "beginner",
        count: int = 5,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Get grammar practice exercises."""
        try:
            questions = llm_client.generate_practice_questions(
                topic=f"grammar - {grammar_point}",
                difficulty=difficulty,
                language=language,
                count=count
            )
            return questions
        except Exception as e:
            return self._get_fallback_grammar(grammar_point, count)
    
    def _get_fallback_grammar(self, grammar_point: str, count: int) -> List[Dict[str, Any]]:
        """Fallback grammar exercises when LLM is unavailable."""
        basic_grammar = {
            "particles": [
                {
                    "question": "Fill in the blank: 私___学生です。(I am a student)",
                    "type": "fill_blank",
                    "correct_answer": "は",
                    "explanation": "は (wa) is the topic particle, marking '私' (I) as the topic of the sentence."
                },
                {
                    "question": "Choose the correct particle: 本___読みます。(I read a book)",
                    "type": "multiple_choice",
                    "options": ["を", "に", "で", "と"],
                    "correct_answer": "を",
                    "explanation": "を (wo) is the direct object particle, marking '本' (book) as the direct object."
                }
            ],
            "verb_conjugation": [
                {
                    "question": "Conjugate '食べる' (to eat) to past tense",
                    "type": "conjugation",
                    "correct_answer": "食べた",
                    "explanation": "食べる is a ru-verb. For past tense, remove る and add た: 食べた"
                }
            ]
        }
        
        exercises = basic_grammar.get(grammar_point, basic_grammar["particles"])
        return random.sample(exercises, min(count, len(exercises)))
    
    def explain_grammar_point(
        self,
        text: str,
        language: str = "en"
    ) -> str:
        """Get detailed explanation of Japanese grammar in the text."""
        try:
            return llm_client.explain_japanese_grammar(text, language)
        except Exception as e:
            return f"Grammar explanation unavailable: {str(e)}"


class ConversationPractice:
    """Conversation practice for Japanese learning."""
    
    def __init__(self):
        """Initialize conversation practice."""
        self.scenarios = [
            "greeting", "restaurant", "shopping", "directions", "introduction",
            "phone_call", "appointment", "complaint", "compliment", "travel"
        ]
    
    def get_conversation_scenario(
        self,
        scenario: str = "greeting",
        difficulty: str = "beginner",
        language: str = "en"
    ) -> Dict[str, Any]:
        """Get a conversation practice scenario."""
        try:
            questions = llm_client.generate_practice_questions(
                topic=f"conversation - {scenario}",
                difficulty=difficulty,
                language=language,
                count=1
            )
            
            if questions:
                return questions[0]
            else:
                return self._get_fallback_conversation(scenario)
                
        except Exception as e:
            return self._get_fallback_conversation(scenario)
    
    def _get_fallback_conversation(self, scenario: str) -> Dict[str, Any]:
        """Fallback conversation scenarios when LLM is unavailable."""
        basic_conversations = {
            "greeting": {
                "question": "Practice basic greetings",
                "type": "conversation",
                "dialogue": [
                    {"speaker": "A", "japanese": "おはようございます", "english": "Good morning", "vietnamese": "Chào buổi sáng"},
                    {"speaker": "B", "japanese": "おはようございます", "english": "Good morning", "vietnamese": "Chào buổi sáng"},
                    {"speaker": "A", "japanese": "今日はいい天気ですね", "english": "It's nice weather today", "vietnamese": "Hôm nay thời tiết đẹp nhỉ"},
                    {"speaker": "B", "japanese": "そうですね", "english": "Yes, it is", "vietnamese": "Đúng vậy"}
                ],
                "explanation": "Basic greeting conversation with weather comment"
            },
            "restaurant": {
                "question": "Ordering at a restaurant",
                "type": "conversation",
                "dialogue": [
                    {"speaker": "Waiter", "japanese": "いらっしゃいませ", "english": "Welcome", "vietnamese": "Xin chào quý khách"},
                    {"speaker": "Customer", "japanese": "メニューをお願いします", "english": "Menu please", "vietnamese": "Cho tôi xem thực đơn"},
                    {"speaker": "Waiter", "japanese": "はい、どうぞ", "english": "Here you are", "vietnamese": "Dạ, mời quý khách"},
                    {"speaker": "Customer", "japanese": "ラーメンをお願いします", "english": "Ramen please", "vietnamese": "Cho tôi một tô ramen"}
                ],
                "explanation": "Basic restaurant ordering conversation"
            }
        }
        
        return basic_conversations.get(scenario, basic_conversations["greeting"])