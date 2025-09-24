"""LLM service for AI interactions with multiple providers."""

from typing import Dict, List, Optional, Any
import asyncio
from abc import ABC, abstractmethod
from enum import Enum

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from ..core.config import settings


class LLMProvider(Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    GEMINI = "gemini"
    GROQ = "groq"
    LOCAL = "local"
    SIMPLE = "simple"


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[str] = None, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the LLM provider."""
        pass


class SimpleProvider(BaseLLMProvider):
    """Simple fallback provider for basic responses."""
    
    def __init__(self):
        self.is_initialized = False
    
    async def initialize(self, model: str = "simple-responder") -> None:
        """Initialize simple provider."""
        self.is_initialized = True
        logger.info("Simple provider initialized")
    
    async def generate_response(self, prompt: str, context: Optional[str] = None, **kwargs) -> str:
        """Generate simple response."""
        full_prompt = f"{context}\n{prompt}" if context else prompt
        
        # Japanese patterns
        japanese_patterns = {
            "こんにちは": "Hello! How can I help you with Japanese?",
            "ありがとう": "You're welcome! 😊",
            "おはよう": "Good morning!",
            "こんばんは": "Good evening!",
            "はい": "I understand!",
            "いいえ": "I see.",
            "すみません": "No problem!",
            "さようなら": "Goodbye! またね！",
        }
        
        for jp, en in japanese_patterns.items():
            if jp in full_prompt:
                return en
        
        # Task-based responses
        if "translate" in full_prompt.lower():
            return "I can help with basic translation, but please configure a proper AI model for better results."
        elif "grammar" in full_prompt.lower() or "explain" in full_prompt.lower():
            return "I can provide basic grammar help, but an AI model would give much better explanations."
        elif "analyze" in full_prompt.lower():
            return "Text analysis is available through the Japanese processor. For AI insights, please configure an AI model."
        else:
            return "I'm a simple responder. Please configure an AI model (like Ollama) for full functionality. Try: ai-nihongo models"


class OllamaProvider(BaseLLMProvider):
    """Ollama local models provider."""
    
    def __init__(self):
        self.client = None
        self.model = "llama3.1"
        self.is_initialized = False
    
    async def initialize(self, model: str = "llama3.1") -> None:
        """Initialize Ollama provider."""
        try:
            import requests
            
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                raise Exception("Ollama not running. Install from https://ollama.ai and run 'ollama serve'")
            
            self.client = "http://localhost:11434"
            self.model = model
            self.is_initialized = True
            
            # Ensure model is available
            await self._ensure_model(model)
            logger.info(f"Ollama provider initialized with model: {model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama provider: {e}")
            raise
    
    async def _ensure_model(self, model: str):
        """Ensure Ollama model is available."""
        import requests
        try:
            # Check if model exists
            response = requests.post(f"{self.client}/api/show", json={"name": model}, timeout=5)
            if response.status_code != 200:
                logger.info(f"Pulling Ollama model: {model}")
                # Pull model (this might take a while for first time)
                response = requests.post(f"{self.client}/api/pull", json={"name": model}, timeout=300)
                if response.status_code != 200:
                    logger.warning(f"Could not pull model {model}")
        except Exception as e:
            logger.warning(f"Could not ensure model {model}: {e}")
    
    async def generate_response(self, prompt: str, context: Optional[str] = None, **kwargs) -> str:
        """Generate response using Ollama."""
        if not self.is_initialized:
            raise Exception("Ollama provider not initialized")
        
        import requests
        
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        # Add Japanese learning context
        system_prompt = """You are a helpful AI assistant specialized in Japanese language learning. 
        You help users learn Japanese by providing clear explanations, translations, and cultural context.
        Be encouraging and provide examples when appropriate."""
        
        final_prompt = f"{system_prompt}\n\nUser: {full_prompt}\n\nAssistant:"
        
        data = {
            "model": self.model,
            "prompt": final_prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 500)
            }
        }
        
        try:
            response = requests.post(f"{self.client}/api/generate", json=data, timeout=30)
            response_data = response.json()
            return response_data.get("response", "No response from Ollama").strip()
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self):
        self.client = None
        self.is_initialized = False
    
    async def initialize(self, model: str = "claude-3-haiku-20240307") -> None:
        """Initialize Anthropic client."""
        try:
            import anthropic
            import os
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise Exception("ANTHROPIC_API_KEY not found in environment variables")
            
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
            self.model = model
            self.is_initialized = True
            logger.info("Anthropic provider initialized")
        except ImportError:
            logger.error("Anthropic package not installed. Install with: pip install anthropic")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {e}")
            raise
    
    async def generate_response(self, prompt: str, context: Optional[str] = None, **kwargs) -> str:
        """Generate response using Anthropic Claude."""
        if not self.is_initialized:
            raise Exception("Anthropic provider not initialized")
        
        system_message = "You are a helpful AI assistant specialized in Japanese language learning. You help users learn Japanese by providing clear explanations, translations, and cultural context."
        
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                system=system_message,
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=kwargs.get("max_tokens", 500)
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class LLMService:
    """Service for managing LLM interactions with multiple providers."""
    
    def __init__(self):
        self.provider: Optional[LLMProvider] = None
        self.provider_instance: Optional[BaseLLMProvider] = None
        self.model = None
        self.is_initialized = False
    
    async def initialize(self, provider: str = "simple", model: Optional[str] = None) -> None:
        """Initialize the LLM service with specified provider."""
        try:
            self.provider = LLMProvider(provider.lower())
        except ValueError:
            logger.error(f"Unknown provider: {provider}")
            self.provider = LLMProvider.SIMPLE
        
        # Initialize the appropriate provider
        if self.provider == LLMProvider.SIMPLE:
            self.provider_instance = SimpleProvider()
        elif self.provider == LLMProvider.OLLAMA:
            self.provider_instance = OllamaProvider()
        elif self.provider == LLMProvider.ANTHROPIC:
            self.provider_instance = AnthropicProvider()
        else:
            # Fallback to simple provider
            self.provider_instance = SimpleProvider()
            self.provider = LLMProvider.SIMPLE
        
        # Initialize the provider instance
        model_to_use = model or self._get_default_model()
        await self.provider_instance.initialize(model_to_use)
        self.is_initialized = True
        logger.info(f"LLM service initialized with {self.provider.value} provider")
    
    def _get_default_model(self) -> str:
        """Get default model for the provider."""
        defaults = {
            LLMProvider.OLLAMA: "llama3.1",
            LLMProvider.ANTHROPIC: "claude-3-haiku-20240307",
            LLMProvider.SIMPLE: "simple-responder"
        }
        return defaults.get(self.provider, "simple-responder")
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response using the configured provider."""
        if not self.is_initialized or not self.provider_instance:
            raise Exception("LLM service not initialized")
        
        try:
            return await self.provider_instance.generate_response(prompt, context, **kwargs)
        except Exception as e:
            logger.error(f"LLM generation failed with provider {self.provider.value}: {e}")
            raise
    
    async def translate_text(self, text: str, target_language: str = "en") -> str:
        """Translate text to target language."""
        prompt = f"Translate the following text to {target_language}. Only provide the translation:\n\n{text}"
        return await self.generate_response(prompt)
    
    async def explain_grammar(self, text: str, analysis: Optional[Dict[str, Any]] = None) -> str:
        """Explain the grammar of Japanese text."""
        prompt = f"""
        Please explain the grammar of this Japanese text in detail:
        
        Text: {text}
        
        Analysis data: {analysis if analysis else 'No linguistic analysis available'}
        
        Provide a clear explanation suitable for Japanese language learners.
        """
        return await self.generate_response(prompt)