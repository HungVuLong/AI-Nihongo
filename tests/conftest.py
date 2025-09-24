"""Test configuration and fixtures."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from ai_nihongo.core.agent import AIAgent
from ai_nihongo.core.config import Settings


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return Settings(
        anthropic_api_key="test_key",
        database_url="sqlite:///:memory:",
        debug=True
    )


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    mock = AsyncMock()
    mock.initialize.return_value = None
    mock.generate_response.return_value = "Test response"
    mock.translate_text.return_value = "Translated text"
    mock.explain_grammar.return_value = "Grammar explanation"
    return mock


@pytest.fixture
def mock_japanese_processor():
    """Mock Japanese processor for testing."""
    mock = AsyncMock()
    mock.initialize.return_value = None
    mock.analyze_text.return_value = {
        "original_text": "こんにちは",
        "tokens": [
            {
                "surface": "こんにちは",
                "pos": "感動詞",
                "pos_detail": "",
                "base_form": "こんにちは",
                "reading": "コンニチハ",
                "pronunciation": "コンニチワ"
            }
        ],
        "pos_tags": ["感動詞"],
        "pronunciations": ["コンニチワ"],
        "meanings": [],
        "difficulty_level": "beginner",
        "kanji_info": [],
        "grammar_patterns": []
    }
    return mock


@pytest.fixture
async def ai_agent(mock_llm_service, mock_japanese_processor):
    """Create an AI agent for testing."""
    agent = AIAgent()
    agent.llm_service = mock_llm_service
    agent.japanese_processor = mock_japanese_processor
    await agent.initialize()
    return agent


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()