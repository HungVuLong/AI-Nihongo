# AI-Nihongo 🇯🇵

Vietnamese-Japanese-English AI Language Learning Application

A comprehensive language learning tool powered by LLM technology for practicing Japanese with support for Vietnamese and English translations.

## Features ✨

### 🧠 **AI-Powered Learning**
- **LLM Integration**: Uses OpenAI GPT models for intelligent language processing
- **Multi-language Support**: Vietnamese, Japanese, and English translations
- **Adaptive Content**: AI-generated practice questions and explanations
- **Grammar Analysis**: Detailed explanations of Japanese grammar points

### 📚 **Vocabulary Practice**
- **Flashcard System**: Interactive vocabulary learning with spaced repetition
- **Topic-based Learning**: Daily life, food, family, work, travel, and more
- **Multiple Difficulty Levels**: Beginner, intermediate, and advanced
- **Quiz Mode**: Test your knowledge with multiple choice and fill-in-the-blank questions

### 📝 **Grammar Exercises**
- **Particle Practice**: Master Japanese particles (は, を, に, etc.)
- **Verb Conjugation**: Practice various verb forms and tenses
- **Sentence Structure**: Learn proper Japanese sentence patterns
- **Interactive Exercises**: Fill-in-the-blank and multiple choice questions

### 💬 **Conversation Practice**
- **Real-world Scenarios**: Restaurant, shopping, greetings, directions
- **Dialogue Practice**: Interactive conversation simulations
- **Cultural Context**: Learn appropriate language use in different situations
- **Pronunciation Guide**: Romanization and phonetic support

### 🔄 **Translation Tools**
- **Instant Translation**: Quick translation between Vietnamese, Japanese, and English
- **Context-aware**: Considers context for more accurate translations
- **Grammar Explanations**: Understand the structure of translated text
- **Batch Processing**: Translate multiple phrases at once

## Installation 🚀

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (for full functionality)

### Quick Start

1. **Clone the repository**:
```bash
git clone https://github.com/HungVuLong/AI-Nihongo.git
cd AI-Nihongo
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env file and add your OpenAI API key
```

4. **Run the application**:
```bash
python main.py
```

## Configuration ⚙️

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Application Settings
DEFAULT_LANGUAGE=en
DEBUG=false
LOG_LEVEL=INFO

# Japanese Learning Settings
DIFFICULTY_LEVEL=beginner
PRACTICE_SESSION_LENGTH=10
```

### API Key Setup

1. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
2. Add it to your `.env` file
3. The application will work with limited functionality without an API key using fallback data

## Usage 📖

### Interactive Mode (Default)

Run the main application for a full interactive experience:

```bash
python main.py
```

Navigate through the menu to:
- 📚 Practice vocabulary with flashcards and quizzes
- 📝 Complete grammar exercises  
- 💬 Practice conversations in various scenarios
- 🔄 Translate text between languages
- ⚙️ Adjust settings and preferences

### Command Line Interface

Quick access to specific features:

```bash
# Quick translation
python main.py translate --text "Hello" --source en --target ja

# Generate vocabulary set
python main.py vocab --topic daily_life --count 10 --difficulty beginner

# Run demo
python main.py demo

# Create sample data
python main.py --create-sample-data
```

### Example Session

```
Welcome to AI-Nihongo! 🇯🇵

Main Menu:
1. 📚 Vocabulary Practice
2. 📝 Grammar Exercises
3. 💬 Conversation Practice
4. 🔄 Translation
5. ⚙️ Settings
6. ❌ Exit

Choose an option: 1

📚 Vocabulary Practice

Available topics:
1. Daily Life
2. Food  
3. Family
4. Work
5. Travel

Choose a topic: 1
Number of words to practice: 5

📇 Flashcard Practice

Card 1/5
┌─ Japanese ─┐
│ おはよう    │
└────────────┘

Press Enter for answer: 

┌─ Answer ─┐
│ English: Good morning │
│ Vietnamese: Chào buổi sáng │
│ Hiragana: おはよう │
└─────────┘
```

## Project Structure 🏗️

```
AI-Nihongo/
├── src/ai_nihongo/           # Main application package
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Configuration management
│   │   └── __init__.py
│   ├── llm/                  # LLM integration
│   │   ├── client.py         # OpenAI API client
│   │   └── __init__.py
│   ├── practice/             # Learning exercises
│   │   ├── exercises.py      # Vocabulary, grammar, conversation
│   │   └── __init__.py
│   ├── ui/                   # User interface
│   │   ├── cli.py            # Command-line interface
│   │   └── __init__.py
│   ├── utils/                # Utility functions
│   │   ├── helpers.py        # Helper functions
│   │   └── __init__.py
│   ├── data/                 # Data storage
│   └── __init__.py
├── data/                     # Sample data and user progress
│   └── sample_data.json      # Fallback vocabulary and examples
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment configuration template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Dependencies 📦

### Core Requirements
- **openai**: OpenAI API integration
- **requests**: HTTP requests
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and settings

### User Interface
- **rich**: Beautiful terminal output
- **click**: Command-line interface framework
- **colorama**: Cross-platform colored terminal text

### Natural Language Processing
- **transformers**: Hugging Face transformers (optional)
- **torch**: PyTorch (for local models)
- **jieba**: Chinese text segmentation
- **MeCab-python3**: Japanese morphological analyzer
- **fugashi**: MeCab wrapper
- **unidic-lite**: Japanese dictionary

### Data Processing
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **datasets**: Dataset management

## Features Overview 🎯

### Vocabulary Learning
- **12 Topic Categories**: Daily life, food, family, work, travel, nature, emotions, colors, numbers, time, weather, shopping
- **3 Difficulty Levels**: Beginner (hiragana focus), intermediate (mixed), advanced (kanji emphasis)
- **Multiple Practice Modes**: Flashcards, quizzes, spaced repetition
- **Progress Tracking**: Track learned words and success rates

### Grammar Practice
- **Comprehensive Coverage**: Particles, verb conjugation, adjectives, sentence structure
- **Interactive Exercises**: Fill-in-the-blank, multiple choice, conjugation practice
- **Detailed Explanations**: Grammar rules and usage examples
- **Politeness Levels**: Casual vs formal speech patterns

### Conversation Scenarios
- **Real-world Situations**: Restaurant, shopping, introductions, phone calls
- **Cultural Context**: Appropriate language for different social situations
- **Interactive Practice**: Role-play exercises with AI feedback
- **Progressive Difficulty**: From basic greetings to complex conversations

### Translation Engine
- **Accurate Translations**: Context-aware translation between Vietnamese, Japanese, English
- **Grammar Analysis**: Breakdown of sentence structure and grammar points
- **Bidirectional Support**: Translate in any direction between the three languages
- **Batch Translation**: Process multiple phrases or sentences at once

## AI Integration 🤖

### OpenAI GPT Integration
- **Intelligent Content Generation**: Create contextual practice questions
- **Natural Language Understanding**: Analyze Japanese text for grammar explanations
- **Adaptive Learning**: Adjust difficulty based on user performance
- **Cultural Context**: Provide cultural insights and usage notes

### Fallback Support
- **Offline Functionality**: Works without internet using pre-loaded data
- **Sample Data**: Comprehensive vocabulary sets and conversation examples
- **Local Processing**: Basic text analysis and practice generation

## Contributing 🤝

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Setup

```bash
# Clone the repository
git clone https://github.com/HungVuLong/AI-Nihongo.git
cd AI-Nihongo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run the application
python main.py
```

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- **OpenAI** for providing the GPT API
- **Japanese Language Community** for vocabulary and grammar resources
- **Vietnamese-Japanese Learning Community** for cultural insights
- **Open Source Contributors** for various language processing tools

## Support 💬

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/HungVuLong/AI-Nihongo/issues)
- **Discussions**: Join our [GitHub Discussions](https://github.com/HungVuLong/AI-Nihongo/discussions)
- **Documentation**: Check our [Wiki](https://github.com/HungVuLong/AI-Nihongo/wiki) for detailed guides

## Roadmap 🗺️

### Version 1.1 (Planned)
- [ ] **Voice Recognition**: Practice pronunciation with speech-to-text
- [ ] **Writing Practice**: Kanji stroke order and writing exercises
- [ ] **Progress Analytics**: Detailed learning statistics and reports
- [ ] **Custom Vocabulary**: Create and import personal vocabulary lists

### Version 1.2 (Future)
- [ ] **Mobile App**: React Native mobile application
- [ ] **Web Interface**: Browser-based learning platform
- [ ] **Multiplayer Mode**: Practice with other learners
- [ ] **Advanced AI**: Fine-tuned models for Japanese language learning

### Version 2.0 (Vision)
- [ ] **Multi-language Expansion**: Support for Korean, Chinese, and other Asian languages
- [ ] **VR/AR Integration**: Immersive language learning experiences
- [ ] **AI Tutor**: Personalized AI teaching assistant
- [ ] **Community Features**: Share progress and compete with friends

---

**Start your Japanese learning journey today!** 🌸

```bash
python main.py
```

がんばって！ (Ganbatte! - Good luck!)