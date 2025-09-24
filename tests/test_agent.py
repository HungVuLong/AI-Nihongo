"""Tests for the AI Agent."""

import pytest
from unittest.mock import AsyncMock

from ai_nihongo.core.agent import AIAgent


class TestAIAgent:
    """Test cases for AI Agent."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, ai_agent):
        """Test agent initialization."""
        assert ai_agent.is_initialized is True
        assert ai_agent.llm_service is not None
        assert ai_agent.japanese_processor is not None
    
    @pytest.mark.asyncio
    async def test_process_message(self, ai_agent):
        """Test message processing."""
        message = "こんにちは"
        response = await ai_agent.process_message(message)
        
        assert response == "Test response"
        ai_agent.llm_service.generate_response.assert_called_once()
        ai_agent.japanese_processor.analyze_text.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_analyze_japanese_text(self, ai_agent):
        """Test Japanese text analysis."""
        text = "こんにちは"
        analysis = await ai_agent.analyze_japanese_text(text)
        
        assert analysis["original_text"] == text
        assert "tokens" in analysis
        assert analysis["difficulty_level"] == "beginner"
        ai_agent.japanese_processor.analyze_text.assert_called_once_with(text)
    
    @pytest.mark.asyncio
    async def test_translate_text(self, ai_agent):
        """Test text translation."""
        text = "Hello"
        result = await ai_agent.translate_text(text, "ja")
        
        assert result == "Translated text"
        ai_agent.llm_service.translate_text.assert_called_once_with(text, "ja")
    
    @pytest.mark.asyncio
    async def test_explain_grammar(self, ai_agent):
        """Test grammar explanation."""
        text = "これは本です"
        explanation = await ai_agent.explain_grammar(text)
        
        assert explanation == "Grammar explanation"
        ai_agent.japanese_processor.analyze_text.assert_called_once_with(text)
        ai_agent.llm_service.explain_grammar.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_conversation_history(self, ai_agent):
        """Test conversation history storage."""
        user_id = "test_user"
        message = "こんにちは"
        
        # Process multiple messages
        await ai_agent.process_message(message, user_id=user_id)
        await ai_agent.process_message("元気ですか？", user_id=user_id)
        
        # Check history
        history = ai_agent._get_recent_history(user_id)
        assert len(history) == 2
        assert history[0]["content"] == message