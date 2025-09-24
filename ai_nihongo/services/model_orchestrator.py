"""Intelligent model orchestration for different tasks."""

from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio
import time

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from ..services.llm_service import LLMService
from ..services.translation_service import TranslationService


class TaskType(Enum):
    """Different types of tasks requiring different models."""
    CHAT = "chat"                    # Casual conversation
    TRANSLATION = "translation"     # Text translation
    GRAMMAR_ANALYSIS = "grammar"     # Grammar explanation
    TEXT_ANALYSIS = "analysis"      # Text structure analysis
    QUICK_RESPONSE = "quick"        # Fast simple responses
    CREATIVE_WRITING = "creative"   # Story writing, examples


class ModelOrchestrator:
    """Orchestrates multiple models for optimal performance."""
    
    def __init__(self):
        self.models: Dict[str, LLMService] = {}
        self.task_preferences: Dict[TaskType, List[str]] = {}
        self.model_capabilities: Dict[str, Dict[str, float]] = {}
        self.translation_service = TranslationService()
        self.is_initialized = False
        self.setup_default_preferences()
    
    def setup_default_preferences(self):
        """Setup default model preferences for each task."""
        self.task_preferences = {
            TaskType.CHAT: ["ollama", "groq", "anthropic", "simple"],
            TaskType.TRANSLATION: ["anthropic", "gemini", "ollama", "groq", "simple"],
            TaskType.GRAMMAR_ANALYSIS: ["anthropic", "gemini", "ollama", "simple"],
            TaskType.TEXT_ANALYSIS: ["local", "ollama", "simple"],  # Can run without API
            TaskType.QUICK_RESPONSE: ["groq", "simple", "local"],
            TaskType.CREATIVE_WRITING: ["ollama", "anthropic", "gemini", "groq", "simple"]
        }
        
        # Model performance scores (0-1)
        self.model_capabilities = {
            "ollama": {"speed": 0.7, "quality": 0.8, "japanese": 0.7, "cost": 1.0},
            "anthropic": {"speed": 0.8, "quality": 0.9, "japanese": 0.85, "cost": 0.2},
            "gemini": {"speed": 0.8, "quality": 0.9, "japanese": 0.8, "cost": 0.8},
            "groq": {"speed": 0.95, "quality": 0.8, "japanese": 0.7, "cost": 0.9},
            "huggingface": {"speed": 0.6, "quality": 0.7, "japanese": 0.6, "cost": 1.0},
            "local": {"speed": 0.9, "quality": 0.5, "japanese": 0.3, "cost": 1.0},
            "simple": {"speed": 1.0, "quality": 0.2, "japanese": 0.4, "cost": 1.0}
        }
    
    async def initialize(self):
        """Initialize all available models."""
        # Initialize translation service
        await self.translation_service.initialize()
        
        available_providers = self._get_available_providers()
        
        for provider in available_providers:
            try:
                service = LLMService()
                await service.initialize(provider=provider)
                self.models[provider] = service
                logger.info(f"✅ Initialized {provider} model")
            except Exception as e:
                logger.warning(f"❌ Failed to initialize {provider}: {e}")
                continue
        
        if not self.models:
            # Ensure we have at least a simple responder
            simple_service = LLMService()
            await simple_service.initialize(provider="simple")
            self.models["simple"] = simple_service
            logger.info("✅ Fallback to simple responder")
        
        self.is_initialized = True
    
    async def process_task(
        self, 
        task_type: TaskType,
        content: str, 
        context: Optional[Dict[str, Any]] = None,
        fallback: bool = True
    ) -> str:
        """
        Process task using the best available model.
        
        Args:
            task_type: Type of task
            content: Input text
            context: Additional context dictionary
            fallback: Whether to fallback to other models if primary fails
            
        Returns:
            String response from the model
        """
        # Handle translation tasks specially with dedicated translation service
        if task_type == TaskType.TRANSLATION:
            return await self._handle_translation_task(content, context)
        
        preferred_models = self.task_preferences.get(task_type, ["simple"])
        
        for model_name in preferred_models:
            if model_name not in self.models:
                continue
            
            try:
                logger.info(f"🤖 Using {model_name} for {task_type.value} task")
                
                model = self.models[model_name]
                # Extract japanese_analysis from context if available
                japanese_context = context.get("japanese_analysis") if context else None
                response = await model.generate_response(content, context=japanese_context)
                
                return response
                
            except Exception as e:
                logger.warning(f"❌ {model_name} failed for {task_type.value}: {e}")
                if not fallback:
                    raise
                continue
        
        # If all models failed, return error
        return f"Sorry, no models available for {task_type.value} task."
    
    async def chat_with_best_model(self, message: str, context: Optional[str] = None) -> str:
        """Chat using the best available chat model."""
        result = await self.process_task(message, TaskType.CHAT, context)
        return result["response"]
    
    async def translate_with_best_model(self, text: str, target_lang: str = "en") -> str:
        """Translate using the best translation model."""
        prompt = f"Translate this Japanese text to {target_lang}: {text}"
        result = await self.process_task(prompt, TaskType.TRANSLATION)
        return result["response"]
    
    async def analyze_grammar_with_best_model(self, text: str) -> str:
        """Analyze grammar using the best analysis model."""
        prompt = f"Explain the Japanese grammar in this text: {text}"
        result = await self.process_task(prompt, TaskType.GRAMMAR_ANALYSIS)
        return result["response"]
    
    async def quick_response(self, text: str) -> str:
        """Get quick response using fastest model."""
        result = await self.process_task(text, TaskType.QUICK_RESPONSE)
        return result["response"]
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models."""
        status = {}
        for name, model in self.models.items():
            status[name] = {
                "initialized": hasattr(model, 'client') and model.client is not None,
                "provider": getattr(model, 'provider', None),
                "model": getattr(model, 'model', None),
                "capabilities": self.model_capabilities.get(name, {})
            }
        return status
    
    def _get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        available = ["simple"]  # Always available
        
        try:
            import requests
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                available.append("ollama")
        except:
            pass
        
        try:
            import transformers
            available.extend(["huggingface", "local"])
        except ImportError:
            pass
        
        try:
            import google.generativeai
            import os
            if os.getenv("GEMINI_API_KEY"):
                available.append("gemini")
        except ImportError:
            pass
        
        try:
            import os
            if os.getenv("GROQ_API_KEY"):
                available.append("groq")
        except ImportError:
            pass
        
        try:
            import anthropic
            import os
            if os.getenv("ANTHROPIC_API_KEY"):
                available.append("anthropic")
        except ImportError:
            pass
        
        return available
    
    def set_task_preference(self, task_type: TaskType, models: List[str]):
        """Set model preference for a specific task."""
        self.task_preferences[task_type] = models
        logger.info(f"Updated preferences for {task_type.value}: {models}")
    
    async def benchmark_models(self, test_prompt: str = "こんにちは") -> Dict[str, Any]:
        """Benchmark all available models."""
        results = {}
        
        for model_name in self.models.keys():
            try:
                start_time = time.time()
                
                model = self.models[model_name]
                response = await model.generate_response(test_prompt)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                results[model_name] = {
                    "response_time": response_time,
                    "success": True,
                    "response_length": len(response),
                    "capabilities": self.model_capabilities.get(model_name, {})
                }
                
            except Exception as e:
                results[model_name] = {
                    "error": str(e),
                    "success": False,
                    "response_time": float('inf')
                }
        
        return results
    
    async def get_available_models(self) -> List[str]:
        """Get list of available model names."""
        return list(self.models.keys())
    
    async def _handle_translation_task(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle translation tasks using dedicated translation service."""
        try:
            # Parse translation request
            # Common patterns: "Translate X", "What does X mean", "X in English"
            content_lower = content.lower()
            
            # Extract target language and text to translate
            target_lang = "en"  # Default
            text_to_translate = content
            
            # Simple parsing logic
            if "translate to japanese" in content_lower or "in japanese" in content_lower:
                target_lang = "ja"
            elif "translate to english" in content_lower or "in english" in content_lower or "mean" in content_lower:
                target_lang = "en"
            
            # Extract the actual text to translate (after "translate" keyword)
            if "translate" in content_lower:
                # Find the text after "translate"
                parts = content.split("translate", 1)
                if len(parts) > 1:
                    text_part = parts[1].strip()
                    # Remove common prefixes like "to english:", ":", etc.
                    for prefix in [f"to {target_lang}:", "to japanese:", "to english:", ":"]:
                        if text_part.lower().startswith(prefix):
                            text_part = text_part[len(prefix):].strip()
                            break
                    if text_part:
                        text_to_translate = text_part
            elif "what does" in content_lower and "mean" in content_lower:
                # Extract text between "what does" and "mean"
                start = content_lower.find("what does") + len("what does")
                end = content_lower.find("mean")
                if start < end:
                    text_to_translate = content[start:end].strip()
            
            # Auto-detect source language if not specified
            source_lang = "auto"
            if context and context.get("japanese_analysis"):
                # If Japanese analysis exists, it's likely Japanese text
                source_lang = "ja"
            
            # Perform translation
            result = await self.translation_service.translate(
                text=text_to_translate,
                target_lang=target_lang,
                source_lang=source_lang,
                context=context
            )
            
            # Format the response
            if result.get("confidence", 0) > 0.5:
                response = f"Translation: {result['translated_text']}"
                if result.get("provider") != "simple":
                    response += f"\n(via {result['provider']} translation)"
                if result.get("note"):
                    response += f"\nNote: {result['note']}"
                return response
            else:
                return f"I couldn't translate '{text_to_translate}'. Try installing Google Translate support: pip install googletrans==4.0.0-rc1"
        
        except Exception as e:
            logger.error(f"Translation task failed: {e}")
            return f"Translation failed: {str(e)}"