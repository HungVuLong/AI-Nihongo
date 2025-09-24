# AI-Nihongo Getting Started Guide

## Overview

AI-Nihongo is an AI agent designed for Japanese language learning and processing. It provides:

- Interactive chat with AI tutor
- Japanese text analysis and tokenization
- Translation between Japanese and other languages
- Grammar explanations
- REST API for integration

## Quick Start

### 1. Basic Chat (CLI)

Start an interactive chat session:

```bash
ai-nihongo chat
```

Or send a single message:

```bash
ai-nihongo chat -m "こんにちは！"
```

### 2. Text Analysis

Analyze Japanese text:

```bash
ai-nihongo analyze "私は学生です。"
```

This will show:
- Token breakdown
- Part-of-speech tags
- Difficulty level
- Kanji information

### 3. Translation

Translate text:

```bash
# Japanese to English
ai-nihongo translate "こんにちは" -t en

# English to Japanese  
ai-nihongo translate "Hello" -t ja
```

### 4. Grammar Explanation

Get grammar explanations:

```bash
ai-nihongo explain "本を読んでいます。"
```

### 5. API Server

Start the REST API server:

```bash
ai-nihongo server
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Programming Usage

### Basic Python Usage

```python
import asyncio
from ai_nihongo import AIAgent

async def main():
    # Create and initialize agent
    agent = AIAgent()
    await agent.initialize()
    
    # Chat with the agent
    response = await agent.process_message("こんにちは！")
    print(f"AI: {response}")
    
    # Analyze Japanese text
    analysis = await agent.analyze_japanese_text("私は学生です。")
    print(f"Difficulty: {analysis['difficulty_level']}")

asyncio.run(main())
```

### API Usage

```python
import requests

# Chat endpoint
response = requests.post("http://localhost:8000/chat", json={
    "message": "こんにちは！",
    "user_id": "user123"
})
print(response.json()["response"])

# Analysis endpoint
response = requests.post("http://localhost:8000/analyze", json={
    "text": "私は学生です。"
})
analysis = response.json()
print(f"Tokens: {len(analysis['tokens'])}")
```

## Configuration

### Environment Variables

Create a `.env` file:

```env
# API Keys (at least one required)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Model Settings
DEFAULT_MODEL=gpt-4
MAX_TOKENS=2000
TEMPERATURE=0.7

# Japanese Processing
TOKENIZER_MODEL=mecab  # or 'sudachi'
SUDACHI_DICT_TYPE=core
```

### Using Different Models

```python
from ai_nihongo.core.config import settings

# Use different OpenAI model
settings.default_model = "gpt-3.5-turbo"

# Use Anthropic Claude
agent = AIAgent()
response = await agent.llm_service.generate_response(
    message="Hello", 
    provider="anthropic"
)
```

## Features in Detail

### Japanese Text Analysis

The text analysis provides:

- **Tokenization**: Break text into meaningful units
- **POS Tagging**: Part-of-speech for each token
- **Pronunciation**: Readings for Japanese text
- **Difficulty Assessment**: Beginner/Intermediate/Advanced
- **Kanji Information**: Details about kanji characters
- **Grammar Patterns**: Common grammar structures

### Supported Languages

- **Primary**: Japanese ↔ English
- **Additional**: Any language supported by the underlying LLM

### AI Models

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3 models
- **Fallback**: Automatic switching if primary model fails

## Best Practices

### For Learning

1. **Start Simple**: Begin with basic greetings and common phrases
2. **Ask for Explanations**: Use the explain command for grammar help
3. **Practice Regularly**: Use the interactive chat for daily practice
4. **Analyze Mistakes**: Use text analysis to understand errors

### For Development

1. **Use Virtual Environments**: Keep dependencies isolated
2. **Set API Keys**: Always configure your API keys properly
3. **Handle Errors**: Implement proper error handling for API calls
4. **Monitor Usage**: Be aware of API usage and costs

### For Production

1. **Configure Logging**: Set appropriate log levels
2. **Use Environment Variables**: Don't hardcode sensitive information
3. **Implement Rate Limiting**: Protect against abuse
4. **Monitor Performance**: Track response times and errors

## Troubleshooting

### Common Issues

1. **"No API key found"**
   - Check your `.env` file
   - Verify environment variables are loaded

2. **Tokenizer errors**
   - Install Japanese processing libraries:
     ```bash
     pip install fugashi unidic-lite
     ```

3. **API connection errors**
   - Check your internet connection
   - Verify API keys are valid
   - Check API service status

4. **Import errors**
   - Ensure all dependencies are installed
   - Check Python version (3.8+ required)

### Getting Help

- Check the [examples](../examples/) directory
- Review the [API documentation](api.md)
- Open an issue on GitHub for bugs
- Join our community discussions

## Next Steps

- Explore the [examples](../examples/) directory
- Read the [API documentation](api.md)
- Check out advanced features in the code
- Contribute to the project on GitHub