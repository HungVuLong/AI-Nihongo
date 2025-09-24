# AI-Nihongo Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Methods

### 1. Development Installation

For development or if you want to modify the code:

```bash
# Clone the repository
git clone https://github.com/HungVuLong/AI-Nihongo.git
cd AI-Nihongo

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install in development mode
pip install -e .
```

### 2. Production Installation

```bash
pip install ai-nihongo
```

## Required Dependencies

The core dependencies will be installed automatically:

- `openai`: For OpenAI GPT models
- `anthropic`: For Anthropic Claude models  
- `fastapi`: For the REST API
- `uvicorn`: ASGI server for the API
- `pydantic`: Data validation
- `python-dotenv`: Environment variable management

## Optional Dependencies

For enhanced Japanese language processing:

```bash
# For MeCab tokenizer (recommended)
pip install fugashi unidic-lite

# For SudachiPy tokenizer (alternative)
pip install sudachipy

# For development tools
pip install -e ".[dev]"

# For machine learning features
pip install -e ".[ml]"
```

## Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Verification

Verify the installation:

```bash
# Check CLI
ai-nihongo --help

# Test basic functionality
ai-nihongo config
```

## Troubleshooting

### Common Issues

1. **ImportError for Japanese tokenizers**:
   ```bash
   pip install fugashi unidic-lite
   ```

2. **API key not found**:
   - Make sure your `.env` file is in the project root
   - Check that environment variables are set correctly

3. **Permission errors on Windows**:
   - Run command prompt as administrator
   - Or use `--user` flag: `pip install --user ai-nihongo`

### Platform-Specific Notes

#### Windows
- Make sure to use the correct virtual environment activation script
- Some Japanese tokenizers may require Visual C++ Build Tools

#### macOS
- You may need to install Xcode command line tools:
  ```bash
  xcode-select --install
  ```

#### Linux
- Install required system packages:
  ```bash
  sudo apt-get update
  sudo apt-get install python3-dev build-essential
  ```

## Next Steps

After installation, see:
- [Getting Started Guide](getting_started.md)
- [API Documentation](api.md)
- [Examples](../examples/)