# AI-Nihongo

An intelligent AI agent for Japanese language learning and processing, powered by modern language models.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Features

- **Interactive AI Chat**: Practice Japanese with an AI tutor
- **Text Analysis**: Deep analysis of Japanese text with tokenization, POS tagging, and difficulty assessment
- **Translation**: Bidirectional translation between Japanese and other languages
- **Grammar Explanations**: Detailed explanations of Japanese grammar patterns
- **REST API**: Full-featured API for integration with other applications
- **Multiple LLM Support**: Works with OpenAI GPT and Anthropic Claude models
- **Japanese Processing**: Advanced Japanese text processing with MeCab and SudachiPy

## 📦 Installation

### Quick Install

```bash
pip install ai-nihongo
```

### Development Install

```bash
git clone https://github.com/HungVuLong/AI-Nihongo.git
cd AI-Nihongo
pip install -e .
```

## 🔧 Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Add your API keys to `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## 🎯 Quick Start

### Command Line Interface

```bash
# Interactive chat
ai-nihongo chat

# Analyze Japanese text
ai-nihongo analyze "私は学生です。"

# Translate text
ai-nihongo translate "Hello" -t ja

# Explain grammar
ai-nihongo explain "本を読んでいます。"

# Start API server
ai-nihongo server
```

### Python API

```python
import asyncio
from ai_nihongo import AIAgent

async def main():
    agent = AIAgent()
    await agent.initialize()
    
    # Chat with the AI
    response = await agent.process_message("こんにちは！")
    print(f"AI: {response}")
    
    # Analyze Japanese text
    analysis = await agent.analyze_japanese_text("私は学生です。")
    print(f"Difficulty: {analysis['difficulty_level']}")

asyncio.run(main())
```

### REST API

```bash
# Start the server
ai-nihongo server

# Use the API
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "こんにちは！", "user_id": "user123"}'
```

## 🏗️ Project Structure

```
ai_nihongo/
├── core/                   # Core functionality
│   ├── agent.py           # Main AI agent
│   ├── config.py          # Configuration management
│   └── __init__.py
├── models/                 # Data models
│   ├── conversation.py    # Conversation and message models
│   └── __init__.py
├── services/              # External services
│   ├── llm_service.py     # LLM integration
│   ├── japanese_processor.py  # Japanese text processing
│   └── __init__.py
├── api/                   # REST API
│   ├── main.py           # FastAPI application
│   └── __init__.py
├── cli.py                # Command-line interface
└── __init__.py

tests/                     # Test suite
examples/                  # Usage examples
docs/                     # Documentation
```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Getting Started](docs/getting_started.md)
- [API Documentation](http://localhost:8000/docs) (when server is running)
- [Examples](examples/)

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=ai_nihongo

# Run specific test
pytest tests/test_agent.py
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/HungVuLong/AI-Nihongo.git
cd AI-Nihongo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality

```bash
# Format code
black ai_nihongo tests

# Lint code
flake8 ai_nihongo tests

# Type checking
mypy ai_nihongo
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📋 Requirements

- Python 3.8+
- OpenAI API key (recommended) or Anthropic API key
- Optional: Japanese processing libraries (fugashi, sudachipy)

## 🔄 Supported Models

### OpenAI
- GPT-4
- GPT-3.5-turbo

### Anthropic
- Claude-3 Haiku
- Claude-3 Sonnet
- Claude-3 Opus

## 🌍 Language Support

- **Primary**: Japanese ↔ English
- **Additional**: Any language pair supported by the underlying LLM

## 📈 Roadmap

- [ ] Enhanced grammar pattern recognition
- [ ] Vocabulary learning features
- [ ] Progress tracking and analytics
- [ ] Voice input/output support
- [ ] Mobile app integration
- [ ] Additional language model support

## 🐛 Known Issues

- Japanese tokenizers require additional system dependencies on some platforms
- API rate limiting not implemented (use responsibly)
- Some advanced grammar patterns may not be detected correctly

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- The creators of MeCab and SudachiPy for Japanese text processing
- The Python community for excellent tools and libraries

## 📞 Support

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/HungVuLong/AI-Nihongo/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/HungVuLong/AI-Nihongo/discussions)

---

Made with ❤️ for Japanese language learners