"""Main AI Agent implementation."""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import asyncio

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .config import settings
from ..models.conversation import Conversation, Message
from ..services.llm_service import LLMService
from ..services.japanese_processor import JapaneseProcessor
from ..services.model_orchestrator import ModelOrchestrator, TaskType

# Import JLPT RAG service
try:
    from ..services.jlpt_rag_service import get_jlpt_rag
    JLPT_RAG_AVAILABLE = True
except ImportError:
    logger.warning("JLPT RAG service not available (missing dependencies: chromadb, sentence-transformers)")
    JLPT_RAG_AVAILABLE = False


class BaseAgent(ABC):
    """Base class for AI agents."""
    
    @abstractmethod
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a user message and return a response."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent."""
        pass


class AIAgent(BaseAgent):
    """Main AI agent for Japanese language learning and processing."""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.japanese_processor = JapaneseProcessor()
        self.orchestrator = ModelOrchestrator()
        self.conversation_history: List[Conversation] = []
        self.is_initialized = False
        self.current_provider = "simple"
        
    async def initialize(self, provider: str = "simple", model: Optional[str] = None) -> None:
        """Initialize the agent and its services."""
        if self.is_initialized:
            return
            
        logger.info("Initializing AI Agent...")
        
        try:
            await self.llm_service.initialize(provider=provider, model=model)
            await self.japanese_processor.initialize()
            await self.orchestrator.initialize()
            self.current_provider = provider
            self.is_initialized = True
            logger.info("AI Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Agent: {e}")
            raise
    
    async def process_message(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return an AI response.
        
        Args:
            message: The user's input message
            context: Additional context for processing
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with response and metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.info(f"Processing message: {message[:50]}...")
        
        try:
            # Classify the task
            task_type = self._classify_task(message)
            
            # Analyze Japanese text if present
            japanese_analysis = await self.japanese_processor.analyze_text(message)
            
            # Check if this looks like a JLPT vocabulary query
            jlpt_results = []
            message_lower = message.lower()
            if JLPT_RAG_AVAILABLE and any(word in message_lower for word in ["jlpt", "vocabulary", "vocab", "word", "kanji", "n1", "n2", "n3", "n4", "n5"]):
                try:
                    # Extract search terms from the message
                    search_terms = self._extract_search_terms(message)
                    if search_terms:
                        jlpt_results = await self.search_jlpt_vocabulary(search_terms, n_results=5)
                        logger.info(f"Found {len(jlpt_results)} JLPT vocabulary matches")
                except Exception as e:
                    logger.warning(f"JLPT search failed: {e}")
            
            # Prepare context for processing
            full_context = {
                "japanese_analysis": japanese_analysis,
                "jlpt_results": jlpt_results,
                "conversation_history": self._get_recent_history(user_id),
                "task_type": task_type.value,
                **(context or {})
            }
            
            # Use orchestrator if available and task requires it, otherwise use LLM service
            if self.orchestrator.is_initialized and task_type != TaskType.CHAT:
                response = await self.orchestrator.process_task(
                    task_type=task_type,
                    content=message,
                    context=full_context
                )
                provider_used = f"orchestrated-{task_type.value}"
            else:
                # If we have JLPT results, enhance the response
                if jlpt_results:
                    response = await self._generate_jlpt_enhanced_response(message, jlpt_results, japanese_analysis)
                    provider_used = f"{self.current_provider}-jlpt-enhanced"
                else:
                    response = await self.llm_service.generate_response(
                        message,
                        context=japanese_analysis
                    )
                    provider_used = self.current_provider
            
            # Store conversation
            if user_id:
                self._store_conversation(user_id, message, response)
            
            logger.info("Message processed successfully")
            
            return {
                "response": response,
                "task_type": task_type.value,
                "provider_used": provider_used,
                "japanese_analysis": japanese_analysis,
                "jlpt_results": jlpt_results,
                "context": full_context
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "申し訳ございません。エラーが発生しました。もう一度お試しください。",
                "error": str(e),
                "task_type": "error",
                "provider_used": "error-fallback"
            }
    
    def _extract_search_terms(self, message: str) -> str:
        """Extract search terms from a message for JLPT vocabulary lookup."""
        message_lower = message.lower()
        
        # Remove common question words
        stop_words = ["what", "is", "the", "meaning", "of", "does", "mean", "how", "to", "say", "jlpt", "vocabulary", "word"]
        words = message.split()
        
        # Filter out stop words and short words
        search_words = [word for word in words if word.lower() not in stop_words and len(word) > 1]
        
        # If we have Japanese characters, prioritize those
        japanese_words = [word for word in search_words if any(ord(char) > 127 for char in word)]
        if japanese_words:
            return " ".join(japanese_words[:2])  # Use first 2 Japanese words
        
        # Otherwise use the remaining words
        return " ".join(search_words[:3])  # Use first 3 words
    
    async def _generate_jlpt_enhanced_response(self, message: str, jlpt_results: List[Dict[str, Any]], japanese_analysis: Dict[str, Any]) -> str:
        """Generate a response enhanced with JLPT vocabulary information."""
        if not jlpt_results:
            return await self.llm_service.generate_response(message, context=japanese_analysis)
        
        # Build enhanced prompt with JLPT vocabulary context
        vocab_context = "JLPT Vocabulary Context:\n"
        for i, result in enumerate(jlpt_results[:3], 1):  # Use top 3 results
            vocab_context += f"{i}. {result['original']} ({result['furigana']}) - {result['english']} [JLPT {result['jlpt_level']}]\n"
        
        enhanced_message = f"""User query: {message}

{vocab_context}

Please provide a helpful response incorporating the relevant JLPT vocabulary information above. If the user is asking about specific vocabulary, explain the words with their readings, meanings, and JLPT levels. Be educational and helpful."""
        
        return await self.llm_service.generate_response(enhanced_message, context=japanese_analysis)
    
    def _classify_task(self, message: str) -> TaskType:
        """Classify the type of task from user message."""
        message_lower = message.lower()
        
        # JLPT vocabulary patterns
        if any(word in message_lower for word in ["jlpt", "vocabulary", "vocab", "word", "kanji", "n1", "n2", "n3", "n4", "n5"]):
            if any(word in message_lower for word in ["search", "find", "look for", "what is"]):
                return TaskType.TEXT_ANALYSIS  # Use text analysis for JLPT queries
        
        # Translation patterns
        if any(word in message_lower for word in ["translate", "translation", "mean", "english"]):
            return TaskType.TRANSLATION
        
        # Grammar analysis patterns
        if any(word in message_lower for word in ["grammar", "particle", "explain", "why", "how"]):
            return TaskType.GRAMMAR_ANALYSIS
        
        # Text analysis patterns
        if any(word in message_lower for word in ["analyze", "analysis", "breakdown", "parse"]):
            return TaskType.TEXT_ANALYSIS
        
        # Creative writing patterns
        if any(word in message_lower for word in ["write", "create", "compose", "story", "essay"]):
            return TaskType.CREATIVE_WRITING
        
        # Quick response patterns (short, simple questions)
        if len(message) < 50 and "?" in message:
            return TaskType.QUICK_RESPONSE
        
        # Default to chat
        return TaskType.CHAT
    
    async def analyze_japanese_text(self, text: str) -> Dict[str, Any]:
        """Analyze Japanese text and return detailed information."""
        if not self.is_initialized:
            await self.initialize()
            
        return await self.japanese_processor.analyze_text(text)
    
    async def translate_text(self, text: str, target_language: str = "en") -> str:
        """Translate text to the target language."""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            if self.orchestrator.is_initialized:
                return await self.orchestrator.process_task(
                    task_type=TaskType.TRANSLATION,
                    content=f"Translate to {target_language}: {text}"
                )
            else:
                return await self.llm_service.translate_text(text, target_language)
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return f"Translation failed: {str(e)}"
    
    async def explain_grammar(self, text: str) -> str:
        """Explain the grammar of Japanese text."""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            analysis = await self.japanese_processor.analyze_text(text)
            
            if self.orchestrator.is_initialized:
                context = {"japanese_analysis": analysis}
                return await self.orchestrator.process_task(
                    task_type=TaskType.GRAMMAR_ANALYSIS,
                    content=f"Explain the grammar of: {text}",
                    context=context
                )
            else:
                return await self.llm_service.explain_grammar(text, analysis)
        except Exception as e:
            logger.error(f"Grammar explanation failed: {e}")
            return f"Grammar explanation failed: {str(e)}"
    
    async def search_jlpt_vocabulary(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search JLPT vocabulary using RAG system."""
        if not JLPT_RAG_AVAILABLE:
            logger.warning("JLPT RAG service not available")
            return []
        
        try:
            rag = await get_jlpt_rag()
            return rag.search_vocabulary(query, n_results=n_results)
        except Exception as e:
            logger.error(f"JLPT vocabulary search failed: {e}")
            return []
    
    async def get_jlpt_vocabulary_by_level(self, level: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get vocabulary entries for a specific JLPT level."""
        if not JLPT_RAG_AVAILABLE:
            logger.warning("JLPT RAG service not available")
            return []
        
        try:
            rag = await get_jlpt_rag()
            return rag.get_vocabulary_by_level(level, limit=limit)
        except Exception as e:
            logger.error(f"JLPT vocabulary by level failed: {e}")
            return []
    
    async def find_similar_words(self, word: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find words similar to the given word using JLPT vocabulary."""
        if not JLPT_RAG_AVAILABLE:
            logger.warning("JLPT RAG service not available")
            return []
        
        try:
            rag = await get_jlpt_rag()
            return rag.get_similar_words(word, n_results=n_results)
        except Exception as e:
            logger.error(f"Similar words search failed: {e}")
            return []
    
    async def get_random_jlpt_vocabulary(self, level: Optional[str] = None, count: int = 5) -> List[Dict[str, Any]]:
        """Get random JLPT vocabulary entries."""
        if not JLPT_RAG_AVAILABLE:
            logger.warning("JLPT RAG service not available")
            return []
        
        try:
            rag = await get_jlpt_rag()
            return rag.get_random_vocabulary(jlpt_level=level, count=count)
        except Exception as e:
            logger.error(f"Random JLPT vocabulary failed: {e}")
            return []
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status and capabilities."""
        return {
            "initialized": self.is_initialized,
            "current_provider": self.current_provider,
            "japanese_processor_ready": self.japanese_processor.is_initialized,
            "orchestrator_ready": self.orchestrator.is_initialized,
            "jlpt_rag_available": JLPT_RAG_AVAILABLE,
            "available_models": await self.orchestrator.get_available_models() if self.orchestrator.is_initialized else [],
            "conversation_count": len(self.conversation_history),
            "supported_tasks": [task.value for task in TaskType]
        }
    
    async def set_provider(self, provider: str, model: Optional[str] = None) -> bool:
        """Switch to a different LLM provider."""
        try:
            await self.llm_service.initialize(provider=provider, model=model)
            self.current_provider = provider
            logger.info(f"Switched to provider: {provider}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch provider to {provider}: {e}")
            return False
    
    def _get_recent_history(self, user_id: Optional[str], limit: int = 5) -> List[Dict[str, str]]:
        """Get recent conversation history for a user."""
        if not user_id:
            return []
        
        user_conversations = [
            conv for conv in self.conversation_history 
            if getattr(conv, 'user_id', None) == user_id
        ]
        
        return [
            {"role": "user", "content": conv.user_message}
            for conv in user_conversations[-limit:]
        ]
    
    def _store_conversation(self, user_id: str, user_message: str, ai_response: str) -> None:
        """Store conversation in memory (in production, use a database)."""
        conversation = Conversation(
            user_id=user_id,
            user_message=user_message,
            ai_response=ai_response
        )
        self.conversation_history.append(conversation)
        
        # Keep only recent conversations in memory
        if len(self.conversation_history) > 1000:
            self.conversation_history = self.conversation_history[-500:]