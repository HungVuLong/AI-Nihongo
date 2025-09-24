# Multi-Model Architecture Update

## Overview

The AI Nihongo project has been successfully updated with a multi-model architecture that intelligently routes tasks to the most appropriate AI model based on task type, cost considerations, and model capabilities.

## Key Features

### 1. Multi-Provider Support
- **Simple Provider**: Basic response patterns, always available as fallback
- **Ollama Provider**: Local models (free, private, requires Ollama installation)
- **OpenAI Provider**: GPT models (API key required)
- **Anthropic Provider**: Claude models (API key required)
- **Extensible**: Easy to add Hugging Face, Google Gemini, Groq, etc.

### 2. Intelligent Task Routing
The system automatically classifies user requests into task types:
- **CHAT**: General conversation
- **TRANSLATION**: Language translation
- **GRAMMAR_ANALYSIS**: Grammar explanations
- **TEXT_ANALYSIS**: Japanese text breakdown
- **QUICK_RESPONSE**: Short, simple questions
- **CREATIVE_WRITING**: Story/essay generation

Each task type has preferred model rankings based on:
- **Quality**: Model performance for specific tasks
- **Speed**: Response time requirements
- **Cost**: API costs and free tier availability
- **Japanese Capabilities**: Specialized Japanese language support

### 3. Graceful Degradation
- Automatic fallback to simpler models if preferred models fail
- Always maintains basic functionality with the simple provider
- Error handling ensures the system never completely fails

### 4. Cost Optimization
- **Free First**: Prioritizes free local models (Ollama) for most tasks
- **Smart Routing**: Uses expensive API models only when necessary
- **Fallback Strategy**: Falls back to simple responses if no AI models available

## Architecture Components

### ModelOrchestrator
Central coordination service that:
- Manages multiple LLM providers
- Routes tasks to optimal models
- Handles failover and fallback
- Tracks performance metrics
- Provides benchmarking capabilities

### Enhanced LLMService
Updated to support multiple providers:
- Provider-agnostic interface
- Dynamic provider switching
- Individual provider initialization
- Graceful error handling

### Updated AIAgent
Main agent enhanced with:
- Task classification logic
- Orchestrator integration
- Provider status tracking
- Rich status reporting

### Enhanced CLI
New commands and features:
- `models` - Show available providers and status
- `status` - System status overview
- `setup` - Interactive configuration wizard
- Provider selection: `--provider simple|ollama|openai|anthropic`
- Model selection: `--model model_name`

## Usage Examples

### Basic Usage (Always Works)
```bash
# Uses simple provider (always available)
ai-nihongo chat --provider simple
ai-nihongo analyze "こんにちは"
```

### With Local Models (Free)
```bash
# First install Ollama: https://ollama.ai
# Then pull a model: ollama pull llama3.1
ai-nihongo chat --provider ollama --model llama3.1
ai-nihongo translate "Hello" --target ja --provider ollama
```

### With API Models (Best Quality)
```bash
# Set environment variables first:
# export OPENAI_API_KEY=your_key
# export ANTHROPIC_API_KEY=your_key

ai-nihongo chat --provider openai --model gpt-3.5-turbo
ai-nihongo grammar "私は学生です" --provider anthropic
```

### Automatic Model Selection
```bash
# Uses orchestrator to pick best model for each task
ai-nihongo chat "Translate this: こんにちは"  # Uses translation model
ai-nihongo chat "Explain this grammar: です"  # Uses grammar model
```

## Configuration

### Environment Variables
```bash
# Optional - for API-based models
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Model Preferences
The system uses these default preferences (can be customized):

**TRANSLATION**: ollama → openai → anthropic → simple
**GRAMMAR_ANALYSIS**: ollama → anthropic → openai → simple  
**TEXT_ANALYSIS**: ollama → simple → openai → anthropic
**CREATIVE_WRITING**: openai → anthropic → ollama → simple
**QUICK_RESPONSE**: simple → ollama → openai → anthropic
**CHAT**: ollama → simple → openai → anthropic

## Benefits

### Cost Savings
- Uses free local models (Ollama) whenever possible
- Only calls paid APIs when necessary for quality
- Simple fallback prevents unnecessary API costs

### Improved Quality
- Routes complex tasks to specialized models
- Creative writing → GPT models
- Japanese grammar → Claude models
- Quick questions → Simple responses

### Better User Experience
- Always functional (simple provider fallback)
- Faster responses for simple tasks
- Higher quality for complex tasks
- Rich status information and setup guidance

### Developer Experience
- Easy to add new providers
- Simple task-based routing
- Comprehensive logging and error handling
- Built-in benchmarking and performance tracking

## System Status

Check system status at any time:
```bash
ai-nihongo status
ai-nihongo models
```

## Future Enhancements

The architecture supports easy addition of:
- **Hugging Face models**: Local transformers
- **Google Gemini**: Gemini Pro/Ultra models
- **Groq**: Fast inference API
- **Custom models**: Local fine-tuned models
- **Model caching**: Response caching for efficiency
- **Load balancing**: Multiple instances of same model
- **Cost tracking**: Detailed API usage monitoring

## Migration Notes

Existing functionality remains 100% compatible. The update only adds capabilities:
- All existing commands work unchanged
- Default behavior uses simple provider (same as before)
- New features are opt-in through CLI flags
- No breaking changes to core functionality

## Testing

All core functionality has been tested and verified:
- ✅ Chat functionality with task classification
- ✅ Japanese text analysis with MeCab
- ✅ Multi-provider support
- ✅ Graceful fallback handling
- ✅ Rich CLI interface with status commands
- ✅ Interactive setup wizard
- ✅ Model switching and configuration

The system is ready for production use with enhanced capabilities while maintaining backward compatibility.