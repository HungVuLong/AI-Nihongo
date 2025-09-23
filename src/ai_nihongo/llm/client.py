"""
LLM client for handling OpenAI API interactions.
"""

import openai
from typing import Dict, List, Optional, Any
import json
from ..core.config import config


class LLMClient:
    """Client for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize the LLM client."""
        if not config.openai_api_key:
            self.client = None
            self.model = config.openai_model
            return
            
        openai.api_key = config.openai_api_key
        self.model = config.openai_model
        self.client = openai.OpenAI(api_key=config.openai_api_key)
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response using the LLM."""
        if not self.client:
            raise Exception("OpenAI API key not configured")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str = ""
    ) -> str:
        """Translate text between Vietnamese, Japanese, and English."""
        if not self.client:
            raise Exception("OpenAI API key not configured")
        
        lang_map = {
            "vi": "Vietnamese",
            "ja": "Japanese", 
            "en": "English"
        }
        
        source_language = lang_map.get(source_lang, source_lang)
        target_language = lang_map.get(target_lang, target_lang)
        
        context_prompt = f"\nContext: {context}" if context else ""
        
        prompt = f"""Translate the following text from {source_language} to {target_language}. 
Provide an accurate and natural translation.{context_prompt}

Text to translate: {text}

Translation:"""
        
        messages = [
            {"role": "system", "content": "You are a professional translator specializing in Vietnamese, Japanese, and English languages."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
    
    def explain_japanese_grammar(self, text: str, user_language: str = "en") -> str:
        """Explain Japanese grammar points in the user's preferred language."""
        if not self.client:
            raise Exception("OpenAI API key not configured")
            
        lang_map = {
            "vi": "Vietnamese",
            "ja": "Japanese",
            "en": "English"
        }
        
        explanation_language = lang_map.get(user_language, "English")
        
        prompt = f"""Analyze the following Japanese text and explain the grammar points in {explanation_language}.
Include information about:
1. Grammar structures used
2. Verb forms and conjugations
3. Particles and their functions
4. Sentence patterns
5. Cultural context if relevant

Japanese text: {text}

Please provide a detailed grammatical explanation:"""
        
        messages = [
            {"role": "system", "content": f"You are a Japanese language teacher who explains grammar in {explanation_language}. Provide clear, educational explanations."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Grammar explanation failed: {str(e)}")
    
    def generate_practice_questions(
        self,
        topic: str,
        difficulty: str = "beginner",
        language: str = "en",
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate practice questions for Japanese learning."""
        if not self.client:
            raise Exception("OpenAI API key not configured")
            
        lang_map = {
            "vi": "Vietnamese",
            "ja": "Japanese",
            "en": "English"
        }
        
        instruction_language = lang_map.get(language, "English")
        
        prompt = f"""Generate {count} Japanese practice questions about {topic} for {difficulty} level students.
Provide instructions and explanations in {instruction_language}.

Each question should include:
1. The question text
2. Multiple choice options (if applicable)
3. The correct answer
4. Explanation of the answer

Format the response as JSON with the following structure:
{{
    "questions": [
        {{
            "question": "Question text",
            "type": "multiple_choice" or "fill_blank" or "translation",
            "options": ["A", "B", "C", "D"] (for multiple choice),
            "correct_answer": "Correct answer",
            "explanation": "Explanation of the answer"
        }}
    ]
}}

Topic: {topic}
Difficulty: {difficulty}"""
        
        messages = [
            {"role": "system", "content": f"You are a Japanese language teacher creating practice questions. Respond in valid JSON format with questions in Japanese and explanations in {instruction_language}."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            response_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON, fallback to basic structure if parsing fails
            try:
                return json.loads(response_text)["questions"]
            except json.JSONDecodeError:
                # Fallback: create a simple question from the response
                return [{
                    "question": f"Practice question about {topic}",
                    "type": "open_ended",
                    "correct_answer": response_text,
                    "explanation": f"Generated content about {topic}"
                }]
                
        except Exception as e:
            raise Exception(f"Question generation failed: {str(e)}")


# Global LLM client instance
llm_client = LLMClient()