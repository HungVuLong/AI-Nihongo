"""Command Line Interface for AI Nihongo."""

import asyncio
import sys
from typing import Optional

import typer
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.markdown import Markdown
    from rich.prompt import Confirm
except ImportError:
    # Fallback without rich formatting
    Console = None

from .core.agent import AIAgent
from .core.config import settings

app = typer.Typer(help="AI-powered Japanese language learning assistant")
console = Console() if Console else None

# Global agent instance
agent = AIAgent()


def print_formatted(content: str, title: str = None, style: str = "blue"):
    """Print formatted output using Rich if available."""
    if console:
        if title:
            console.print(Panel(content, title=title, border_style=style))
        else:
            console.print(content, style=style)
    else:
        if title:
            print(f"\n=== {title} ===")
        print(content)


def print_error(message: str):
    """Print error message."""
    if console:
        console.print(f"❌ Error: {message}", style="red")
    else:
        print(f"Error: {message}")


def print_success(message: str):
    """Print success message."""
    if console:
        console.print(f"✅ {message}", style="green")
    else:
        print(f"Success: {message}")


def print_warning(message: str):
    """Print warning message."""
    if console:
        console.print(f"⚠️ Warning: {message}", style="yellow")
    else:
        print(f"Warning: {message}")


def print_info(message: str):
    """Print info message."""
    if console:
        console.print(f"ℹ️ {message}", style="blue")
    else:
        print(f"Info: {message}")


@app.command()
def chat(
    message: Optional[str] = typer.Argument(None, help="Message to send to the AI"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM provider (simple, ollama, anthropic)"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name")
):
    """Interactive chat with the AI assistant."""
    
    async def run_chat():
        try:
            # Initialize agent
            await agent.initialize(provider=provider or "simple", model=model)
            
            if message:
                # Single message mode
                result = await agent.process_message(message)
                print_formatted(
                    result["response"], 
                    title=f"AI Response ({result.get('provider_used', 'unknown')})",
                    style="green"
                )
                
                # Show Japanese analysis if available
                if result.get("japanese_analysis"):
                    analysis = result["japanese_analysis"]
                    if console:
                        table = Table(title="Japanese Analysis")
                        table.add_column("Surface", style="cyan")
                        table.add_column("Reading", style="magenta")
                        table.add_column("POS", style="yellow")
                        table.add_column("Features", style="blue")
                        
                        for token in analysis.get("tokens", [])[:10]:  # Show first 10 tokens
                            table.add_row(
                                token.get("surface", ""),
                                token.get("reading", ""),
                                token.get("part_of_speech", ""),
                                str(token.get("features", [])[:3])  # First 3 features
                            )
                        console.print(table)
                return
            
            # Interactive mode
            print_info("Starting interactive chat mode. Type 'quit' to exit.")
            print_info(f"Using provider: {provider or 'simple'}")
            
            while True:
                try:
                    if console:
                        user_input = console.input("\n[bold blue]You:[/bold blue] ")
                    else:
                        user_input = input("\nYou: ")
                    
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        print_info("Goodbye! またね！")
                        break
                    
                    if user_input.strip():
                        result = await agent.process_message(user_input)
                        print_formatted(
                            result["response"],
                            title=f"AI Assistant ({result.get('task_type', 'chat')} - {result.get('provider_used', 'unknown')})",
                            style="green"
                        )
                
                except KeyboardInterrupt:
                    print_info("\nGoodbye! またね！")
                    break
                except Exception as e:
                    print_error(f"Chat error: {e}")
        
        except Exception as e:
            print_error(f"Failed to initialize: {e}")
            print_info("Try using the simple provider: ai-nihongo chat --provider simple")
            sys.exit(1)
    
    asyncio.run(run_chat())


@app.command()
def analyze(
    text: str = typer.Argument(..., help="Japanese text to analyze"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed analysis")
):
    """Analyze Japanese text."""
    
    async def run_analysis():
        try:
            await agent.initialize()
            analysis = await agent.analyze_japanese_text(text)
            
            if not analysis:
                print_warning("No Japanese text detected or analysis failed")
                return
            
            if console and detailed:
                # Rich formatted detailed analysis
                table = Table(title=f"Analysis of: {text}")
                table.add_column("Surface", style="cyan", no_wrap=True)
                table.add_column("Reading", style="magenta")
                table.add_column("Part of Speech", style="yellow")
                table.add_column("Features", style="blue")
                
                for token in analysis.get("tokens", []):
                    features_str = ", ".join(token.get("features", [])[:3])  # First 3 features
                    table.add_row(
                        token.get("surface", ""),
                        token.get("reading", ""),
                        token.get("part_of_speech", ""),
                        features_str
                    )
                
                console.print(table)
                
                # Summary
                summary = analysis.get("summary", {})
                console.print(f"\n📊 Summary:")
                console.print(f"   Total tokens: {summary.get('token_count', 0)}")
                console.print(f"   Unique words: {summary.get('unique_words', 0)}")
                
            else:
                # Simple text output
                print_formatted(f"Analysis of: {text}", title="Japanese Text Analysis")
                
                tokens = analysis.get("tokens", [])
                print(f"Tokens ({len(tokens)}):")
                for i, token in enumerate(tokens[:20]):  # Show first 20 tokens
                    surface = token.get("surface", "")
                    reading = token.get("reading", "")
                    pos = token.get("part_of_speech", "")
                    print(f"  {i+1:2d}. {surface} ({reading}) - {pos}")
                
                if len(tokens) > 20:
                    print(f"  ... and {len(tokens) - 20} more tokens")
        
        except Exception as e:
            print_error(f"Analysis failed: {e}")
            sys.exit(1)
    
    asyncio.run(run_analysis())


@app.command()
def translate(
    text: str = typer.Argument(..., help="Text to translate"),
    target: str = typer.Option("en", "--target", "-t", help="Target language (en, ja)"),
    source: str = typer.Option("auto", "--source", "-s", help="Source language (auto, en, ja)"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Translation provider (google, simple, anthropic, ollama)")
):
    """Translate text between Japanese and other languages using specialized translation models."""
    
    async def run_translation():
        try:
            await agent.initialize()
            
            # Import translation service directly for more control
            from ai_nihongo.services.translation_service import TranslationService, TranslationProvider
            translation_service = TranslationService()
            await translation_service.initialize()
            
            # Convert string provider to enum if specified
            provider_enum = None
            if provider:
                try:
                    provider_enum = TranslationProvider(provider.lower())
                except ValueError:
                    print_error(f"Unknown translation provider: {provider}")
                    print_info("Available providers: " + ", ".join(translation_service.get_available_providers()))
                    return
            
            # Get context for better translation
            context = {}
            if source == "ja" or source == "auto":
                japanese_analysis = await agent.analyze_japanese_text(text)
                if japanese_analysis:
                    context["japanese_analysis"] = japanese_analysis
            
            # Perform translation
            result = await translation_service.translate(
                text=text,
                target_lang=target,
                source_lang=source,
                provider=provider_enum,
                context=context
            )
            
            # Display results
            if console:
                from rich.table import Table
                table = Table(title="Translation Result")
                table.add_column("Field", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Original", text)
                table.add_row("Translation", result["translated_text"])
                table.add_row("Source Language", result.get("source_language", "unknown"))
                table.add_row("Target Language", result["target_language"])
                table.add_row("Provider", result.get("provider", "unknown"))
                table.add_row("Confidence", f"{result.get('confidence', 0):.2f}")
                
                console.print(table)
                
                if result.get("note"):
                    print_warning(f"Note: {result['note']}")
            else:
                print(f"Original: {text}")
                print(f"Translation ({result['source_language']} → {result['target_language']}): {result['translated_text']}")
                print(f"Provider: {result.get('provider', 'unknown')} (confidence: {result.get('confidence', 0):.2f})")
                
                if result.get("note"):
                    print(f"Note: {result['note']}")
            
        except Exception as e:
            print_error(f"Translation failed: {e}")
            print_info("Try installing Google Translate support: pip install googletrans==4.0.0-rc1")
            sys.exit(1)
    
    asyncio.run(run_translation())


@app.command()
def grammar(
    text: str = typer.Argument(..., help="Japanese text to explain"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM provider")
):
    """Explain Japanese grammar."""
    
    async def run_grammar():
        try:
            await agent.initialize(provider=provider or "simple")
            explanation = await agent.explain_grammar(text)
            
            print_formatted(f"Text: {text}", title="Grammar Analysis")
            print_formatted(explanation, style="blue")
            
        except Exception as e:
            print_error(f"Grammar explanation failed: {e}")
            sys.exit(1)
    
    asyncio.run(run_grammar())


@app.command()
def translation():
    """Show available translation providers and test translation capabilities."""
    
    async def show_translation_info():
        try:
            from ai_nihongo.services.translation_service import TranslationService
            translation_service = TranslationService()
            await translation_service.initialize()
            
            if console:
                from rich.table import Table
                table = Table(title="Translation Providers")
                table.add_column("Provider", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Languages", style="blue")
                table.add_column("Description", style="yellow")
                
                available_providers = translation_service.get_available_providers()
                supported_languages = translation_service.get_supported_languages()
                
                provider_info = {
                    "simple": ("✅ Available", "ja, en", "Built-in dictionary (fast, limited)"),
                    "google": ("🌐 Google Translate", "100+ languages", "High quality, requires internet"),
                    "anthropic": ("🔑 Anthropic Claude", "Many languages", "AI-powered, requires API key"),
                    "ollama": ("🏠 Local AI", "Many languages", "Free local AI models"),
                }
                
                for provider in ["simple", "google", "anthropic", "ollama"]:
                    status, langs, desc = provider_info.get(provider, ("❓ Unknown", "Unknown", "Unknown"))
                    if provider in available_providers:
                        status = "✅ Ready"
                        langs = ", ".join(supported_languages.get(provider, ["unknown"])[:5])
                        if len(supported_languages.get(provider, [])) > 5:
                            langs += ", ..."
                    else:
                        status = "❌ Not Available"
                    
                    table.add_row(provider, status, langs, desc)
                
                console.print(table)
                
                # Test translation examples
                console.print("\n🧪 Testing translation capabilities...")
                
                test_cases = [
                    ("こんにちは", "ja", "en", "Japanese greeting"),
                    ("Thank you", "en", "ja", "English gratitude"),
                    ("私は学生です", "ja", "en", "Japanese sentence")
                ]
                
                for text, src, tgt, description in test_cases:
                    try:
                        result = await translation_service.translate(text, target_lang=tgt, source_lang=src)
                        console.print(f"  {description}: '{text}' → '{result['translated_text']}' ({result.get('provider', 'unknown')})")
                    except Exception as e:
                        console.print(f"  {description}: Failed - {e}")
                
            else:
                print("Translation Providers:")
                available_providers = translation_service.get_available_providers()
                for provider in ["simple", "google", "anthropic", "ollama"]:
                    status = "✅ Available" if provider in available_providers else "❌ Not Available"
                    print(f"  {provider}: {status}")
                
                print("\nTesting basic translations...")
                test_result = await translation_service.translate("こんにちは", target_lang="en")
                print(f"  'こんにちは' → '{test_result['translated_text']}' ({test_result.get('provider', 'unknown')})")
                
        except Exception as e:
            print_error(f"Failed to get translation info: {e}")
    
    asyncio.run(show_translation_info())


@app.command()
def models():
    """Show available AI models and providers."""
    
    async def show_models():
        try:
            await agent.initialize()
            status = await agent.get_status()
            
            if console:
                table = Table(title="AI Models & Providers")
                table.add_column("Provider", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Description", style="blue")
                
                providers = [
                    ("simple", "✅ Available", "Basic responses, always available"),
                    ("ollama", "🤔 Check setup", "Local models (requires Ollama)"),
                    ("anthropic", "🔑 API Key", "Anthropic Claude models"),
                ]
                
                for provider, status_str, desc in providers:
                    table.add_row(provider, status_str, desc)
                
                console.print(table)
                console.print(f"\nCurrent provider: {status['current_provider']}")
                console.print(f"Orchestrator ready: {'✅' if status['orchestrator_ready'] else '❌'}")
                
            else:
                print("Available Providers:")
                print("  simple     - Basic responses (always available)")
                print("  ollama     - Local models (requires Ollama setup)")
                print("  anthropic  - Anthropic Claude models (requires API key)")
                print(f"\nCurrent: {status['current_provider']}")
            
        except Exception as e:
            print_error(f"Failed to get model info: {e}")
    
    asyncio.run(show_models())


@app.command()
def status():
    """Show system status."""
    
    async def show_status():
        try:
            await agent.initialize()
            status = await agent.get_status()
            
            if console:
                table = Table(title="System Status")
                table.add_column("Component", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Details", style="blue")
                
                table.add_row(
                    "Agent",
                    "✅ Ready" if status['initialized'] else "❌ Not Ready",
                    f"Provider: {status['current_provider']}"
                )
                table.add_row(
                    "Japanese Processor",
                    "✅ Ready" if status['japanese_processor_ready'] else "❌ Not Ready",
                    "MeCab tokenizer"
                )
                table.add_row(
                    "Model Orchestrator",
                    "✅ Ready" if status['orchestrator_ready'] else "❌ Not Ready",
                    f"{len(status.get('available_models', []))} models available"
                )
                table.add_row(
                    "Conversations",
                    f"{status.get('conversation_count', 0)} stored",
                    "In-memory storage"
                )
                
                console.print(table)
                
                # Supported tasks
                console.print(f"\nSupported Tasks: {', '.join(status.get('supported_tasks', []))}")
                
            else:
                print("System Status:")
                print(f"  Agent: {'Ready' if status['initialized'] else 'Not Ready'}")
                print(f"  Provider: {status['current_provider']}")
                print(f"  Japanese Processor: {'Ready' if status['japanese_processor_ready'] else 'Not Ready'}")
                print(f"  Model Orchestrator: {'Ready' if status['orchestrator_ready'] else 'Not Ready'}")
                print(f"  Conversations: {status.get('conversation_count', 0)}")
                
        except Exception as e:
            print_error(f"Failed to get status: {e}")
    
    asyncio.run(show_status())


@app.command()
def setup():
    """Interactive setup wizard."""
    
    def run_setup():
        print_info("AI Nihongo Setup Wizard")
        print_info("This will help you configure the system for optimal performance.")
        
        # Check for dependencies
        print("\n1. Checking dependencies...")
        
        # Check MeCab
        try:
            import MeCab
            print_success("MeCab: Available")
        except ImportError:
            print_warning("MeCab: Not available - Japanese analysis will use fallback methods")
        
        # Check Rich
        try:
            from rich import console
            print_success("Rich: Available")
        except ImportError:
            print_warning("Rich: Not available - using basic text formatting")
        
        # Model recommendations
        print("\n2. AI Model Recommendations:")
        print_info("• For basic usage: Keep default 'simple' provider")
        print_info("• For free local AI: Install Ollama from https://ollama.ai")
        print_info("• For best quality: Configure Anthropic API keys")
        
        print("\n3. Translation Options:")
        print_info("• Built-in dictionary: Always available for common phrases")
        print_info("• Google Translate: pip install googletrans==4.0.0-rc1")
        print_info("• AI Translation: Works with any configured LLM provider")
        
        print("\n4. Environment Variables (optional):")
        print("   ANTHROPIC_API_KEY=your_anthropic_key")
        print("   ANTHROPIC_API_KEY=your_anthropic_key")
        
        print("\n5. Usage Examples:")
        print("   ai-nihongo chat --provider simple")
        print("   ai-nihongo analyze 'こんにちは世界'")
        print("   ai-nihongo translate 'Hello world' --target ja")
        print("   ai-nihongo translate 'こんにちは' --provider google")
        print("   ai-nihongo translation  # Show translation providers")
        
        print_success("\nSetup complete! Try: ai-nihongo chat")
    
    run_setup()


@app.command()
def jlpt():
    """JLPT vocabulary search and study tools."""
    
    async def run_jlpt_menu():
        """Interactive JLPT vocabulary menu."""
        try:
            from ai_nihongo.services.jlpt_rag_service import get_jlpt_rag
            
            print_info("Initializing JLPT vocabulary system...")
            rag = await get_jlpt_rag()
            print_success("JLPT vocabulary system ready!")
            
            if console:
                # Rich interactive menu
                from rich.prompt import Prompt, IntPrompt
                from rich.table import Table
                
                while True:
                    console.print("\n📚 JLPT Vocabulary Tools", style="bold blue")
                    
                    menu_options = [
                        "1. Search vocabulary",
                        "2. Get vocabulary by level",
                        "3. Find similar words",
                        "4. Random vocabulary quiz",
                        "5. Level statistics",
                        "6. Exit"
                    ]
                    
                    for option in menu_options:
                        console.print(f"   {option}")
                    
                    try:
                        choice = IntPrompt.ask("\nChoose an option", choices=["1", "2", "3", "4", "5", "6"])
                        
                        if choice == 1:
                            # Search vocabulary
                            query = Prompt.ask("Enter search term (Japanese or English)")
                            n_results = IntPrompt.ask("Number of results", default=10)
                            
                            console.print(f"🔍 Searching for: {query}")
                            results = rag.search_vocabulary(query, n_results=n_results)
                            
                            if results:
                                table = Table(title=f"Search Results for '{query}'")
                                table.add_column("Japanese", style="cyan")
                                table.add_column("Reading", style="magenta")
                                table.add_column("English", style="green")
                                table.add_column("Level", style="yellow")
                                table.add_column("Score", style="blue")
                                
                                for result in results:
                                    table.add_row(
                                        result['original'],
                                        result['furigana'],
                                        result['english'],
                                        result['jlpt_level'],
                                        f"{result['similarity_score']:.3f}"
                                    )
                                
                                console.print(table)
                            else:
                                console.print("No results found.", style="yellow")
                        
                        elif choice == 2:
                            # Get vocabulary by level
                            level = Prompt.ask("Enter JLPT level", choices=["N1", "N2", "N3", "N4", "N5"])
                            limit = IntPrompt.ask("Number of words", default=20)
                            
                            console.print(f"📖 Getting {level} vocabulary...")
                            vocab = rag.get_vocabulary_by_level(level, limit=limit)
                            
                            if vocab:
                                table = Table(title=f"JLPT {level} Vocabulary")
                                table.add_column("Japanese", style="cyan")
                                table.add_column("Reading", style="magenta")
                                table.add_column("English", style="green")
                                
                                for word in vocab:
                                    table.add_row(
                                        word['original'],
                                        word['furigana'],
                                        word['english']
                                    )
                                
                                console.print(table)
                            else:
                                console.print("No vocabulary found.", style="yellow")
                        
                        elif choice == 3:
                            # Find similar words
                            word = Prompt.ask("Enter a word to find similar words")
                            
                            console.print(f"🔄 Finding words similar to: {word}")
                            similar = rag.get_similar_words(word, n_results=8)
                            
                            if similar:
                                table = Table(title=f"Words Similar to '{word}'")
                                table.add_column("Japanese", style="cyan")
                                table.add_column("Reading", style="magenta")
                                table.add_column("English", style="green")
                                table.add_column("Level", style="yellow")
                                table.add_column("Similarity", style="blue")
                                
                                for word_data in similar:
                                    table.add_row(
                                        word_data['original'],
                                        word_data['furigana'],
                                        word_data['english'],
                                        word_data['jlpt_level'],
                                        f"{word_data['similarity_score']:.3f}"
                                    )
                                
                                console.print(table)
                            else:
                                console.print("No similar words found.", style="yellow")
                        
                        elif choice == 4:
                            # Random vocabulary quiz
                            level_choice = Prompt.ask(
                                "Choose level (or 'all' for mixed)", 
                                choices=["N1", "N2", "N3", "N4", "N5", "all"],
                                default="all"
                            )
                            count = IntPrompt.ask("Number of words", default=5)
                            
                            level = None if level_choice == "all" else level_choice
                            
                            console.print(f"🎲 Random vocabulary quiz...")
                            random_vocab = rag.get_random_vocabulary(jlpt_level=level, count=count)
                            
                            if random_vocab:
                                for i, word in enumerate(random_vocab, 1):
                                    panel_content = f"""
Japanese: {word['original']}
Reading: {word['furigana']}
English: {word['english']}
Level: {word['jlpt_level']}
                                    """.strip()
                                    
                                    console.print(Panel(
                                        panel_content,
                                        title=f"Word {i}/{len(random_vocab)}",
                                        border_style="green"
                                    ))
                                    
                                    if i < len(random_vocab):
                                        Prompt.ask("Press Enter for next word", default="")
                            else:
                                console.print("No vocabulary found.", style="yellow")
                        
                        elif choice == 5:
                            # Level statistics
                            console.print("📊 Calculating statistics...")
                            stats = rag.get_level_statistics()
                            
                            if stats:
                                table = Table(title="JLPT Vocabulary Statistics")
                                table.add_column("Level", style="yellow")
                                table.add_column("Words", style="cyan")
                                table.add_column("Percentage", style="green")
                                
                                for level, data in stats['levels'].items():
                                    table.add_row(
                                        level,
                                        str(data['count']),
                                        f"{data['percentage']}%"
                                    )
                                
                                console.print(table)
                                console.print(f"\nTotal vocabulary: {stats['total_vocabulary']:,} words")
                                console.print(f"Vector database: {stats['collection_count']:,} entries")
                            else:
                                console.print("No statistics available.", style="yellow")
                        
                        elif choice == 6:
                            console.print("👋 Goodbye!", style="yellow")
                            break
                    
                    except KeyboardInterrupt:
                        console.print("\n👋 Goodbye!", style="yellow")
                        break
                    except Exception as e:
                        console.print(f"❌ Error: {e}", style="red")
            
            else:
                # Simple text interface
                print("\nJLPT Vocabulary Tools")
                print("1. Search vocabulary")
                print("2. Get random vocabulary")
                print("3. Level statistics")
                
                while True:
                    try:
                        choice = input("\nChoose option (1-3, or 'q' to quit): ").strip()
                        
                        if choice.lower() in ['q', 'quit', 'exit']:
                            print("Goodbye!")
                            break
                        elif choice == '1':
                            query = input("Enter search term: ")
                            results = rag.search_vocabulary(query, n_results=5)
                            
                            print(f"\nSearch results for '{query}':")
                            for i, result in enumerate(results, 1):
                                print(f"{i}. {result['original']} ({result['furigana']}) - {result['english']} [{result['jlpt_level']}]")
                        
                        elif choice == '2':
                            random_vocab = rag.get_random_vocabulary(count=3)
                            print("\nRandom vocabulary:")
                            for word in random_vocab:
                                print(f"• {word['original']} ({word['furigana']}) - {word['english']} [{word['jlpt_level']}]")
                        
                        elif choice == '3':
                            stats = rag.get_level_statistics()
                            print("\nJLPT Level Statistics:")
                            for level, data in stats['levels'].items():
                                print(f"  {level}: {data['count']} words ({data['percentage']}%)")
                        
                    except KeyboardInterrupt:
                        print("\nGoodbye!")
                        break
                    except Exception as e:
                        print(f"Error: {e}")
        
        except Exception as e:
            print_error(f"Failed to initialize JLPT system: {e}")
            print_info("This might be due to missing dependencies. Try: pip install chromadb sentence-transformers")
            sys.exit(1)
    
    asyncio.run(run_jlpt_menu())


@app.command()
def jlpt_search(
    query: str = typer.Argument(..., help="Search term (Japanese or English)"),
    count: int = typer.Option(10, "--count", "-c", help="Number of results"),
    level: Optional[str] = typer.Option(None, "--level", "-l", help="Filter by JLPT level (N1-N5)")
):
    """Search JLPT vocabulary."""
    
    async def run_search():
        try:
            from ai_nihongo.services.jlpt_rag_service import get_jlpt_rag
            
            print_info(f"Searching for: {query}")
            rag = await get_jlpt_rag()
            
            levels = [level] if level else None
            results = rag.search_vocabulary(query, n_results=count, jlpt_levels=levels)
            
            if results:
                if console:
                    table = Table(title=f"Search Results for '{query}'")
                    table.add_column("Japanese", style="cyan")
                    table.add_column("Reading", style="magenta")
                    table.add_column("English", style="green")
                    table.add_column("Level", style="yellow")
                    table.add_column("Score", style="blue")
                    
                    for result in results:
                        table.add_row(
                            result['original'],
                            result['furigana'],
                            result['english'],
                            result['jlpt_level'],
                            f"{result['similarity_score']:.3f}"
                        )
                    
                    console.print(table)
                else:
                    print(f"\nFound {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        print(f"{i:2d}. {result['original']} ({result['furigana']}) - {result['english']} [{result['jlpt_level']}] ({result['similarity_score']:.3f})")
            else:
                print_warning("No results found")
        
        except Exception as e:
            print_error(f"Search failed: {e}")
            sys.exit(1)
    
    asyncio.run(run_search())


@app.command()
def jlpt_quiz(
    level: Optional[str] = typer.Option(None, "--level", "-l", help="JLPT level (N1-N5)"),
    count: int = typer.Option(5, "--count", "-c", help="Number of words")
):
    """Random JLPT vocabulary quiz."""
    
    async def run_quiz():
        try:
            from ai_nihongo.services.jlpt_rag_service import get_jlpt_rag
            
            level_text = f" ({level})" if level else " (mixed levels)"
            print_info(f"Random vocabulary quiz{level_text}")
            
            rag = await get_jlpt_rag()
            vocab = rag.get_random_vocabulary(jlpt_level=level, count=count)
            
            if vocab:
                for i, word in enumerate(vocab, 1):
                    if console:
                        panel_content = f"""
Japanese: {word['original']}
Reading: {word['furigana']}
English: {word['english']}
Level: {word['jlpt_level']}
                        """.strip()
                        
                        console.print(Panel(
                            panel_content,
                            title=f"Word {i}/{len(vocab)}",
                            border_style="green"
                        ))
                    else:
                        print(f"\nWord {i}/{len(vocab)}:")
                        print(f"  Japanese: {word['original']}")
                        print(f"  Reading: {word['furigana']}")
                        print(f"  English: {word['english']}")
                        print(f"  Level: {word['jlpt_level']}")
                    
                    if i < len(vocab):
                        input("Press Enter for next word...")
            else:
                print_warning("No vocabulary found")
        
        except Exception as e:
            print_error(f"Quiz failed: {e}")
            sys.exit(1)
    
    asyncio.run(run_quiz())


@app.command()
def version():
    """Show version information."""
    print(f"AI Nihongo v{settings.version}")
    print("Japanese Language Learning Assistant")


if __name__ == "__main__":
    app()

import asyncio
from typing import Optional
import sys

try:
    import typer
    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    # Create a simple mock for typer
    class MockTyper:
        def __init__(self, **kwargs): pass
        def command(self, *args, **kwargs): return lambda f: f
        def __call__(self, *args, **kwargs): pass
    typer = MockTyper()

try:
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None
    Prompt = None
    Panel = None
    
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .core.agent import AIAgent
from .core.config import settings


app = typer.Typer(help="AI-Nihongo: AI agent for Japanese language learning")

if RICH_AVAILABLE:
    console = Console()
else:
    console = None


def print_message(message: str, style: str = ""):
    """Print message with optional styling."""
    if console and RICH_AVAILABLE:
        console.print(message, style=style)
    else:
        print(message)


def print_panel(content: str, title: str = "", border_style: str = "blue"):
    """Print content in a panel."""
    if console and RICH_AVAILABLE:
        console.print(Panel(content, title=title, border_style=border_style))
    else:
        print(f"\n{title}\n{'-' * len(title)}\n{content}\n")


@app.command()
def chat(
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i", help="Start interactive chat"),
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Single message to process")
):
    """Chat with the AI agent."""
    
    async def run_chat():
        agent = AIAgent()
        
        try:
            print_message("🤖 Initializing AI-Nihongo...", "blue")
            await agent.initialize()
            print_message("✅ AI-Nihongo initialized successfully!", "green")
            
            if message:
                # Single message mode
                print_panel(f"User: {message}", "Input", "green")
                response = await agent.process_message(message)
                print_panel(response, "AI Response", "blue")
                return
            
            if interactive:
                # Interactive mode
                print_message("\n💬 Interactive Chat Mode", "bold blue")
                print_message("Type 'exit', 'quit', or 'bye' to end the conversation.", "dim")
                print_message("Type 'help' for available commands.\n", "dim")
                
                while True:
                    try:
                        if RICH_AVAILABLE and console:
                            user_input = Prompt.ask("[bold green]You[/bold green]")
                        else:
                            user_input = input("You: ")
                        
                        if user_input.lower() in ['exit', 'quit', 'bye']:
                            print_message("👋 Goodbye!", "yellow")
                            break
                        
                        if user_input.lower() == 'help':
                            help_text = """
Available commands:
- exit, quit, bye: End the conversation
- help: Show this help message
- Any other text: Chat with the AI agent

The AI can help with:
- Japanese language learning
- Text translation
- Grammar explanations
- Vocabulary analysis
                            """
                            print_panel(help_text.strip(), "Help", "yellow")
                            continue
                        
                        if not user_input.strip():
                            continue
                        
                        try:
                            print_message("🤔 Thinking...", "dim")
                            response = await agent.process_message(user_input)
                            print_panel(response, "AI", "blue")
                        except Exception as e:
                            print_message(f"❌ Error: {e}", "red")
                    except (EOFError, KeyboardInterrupt):
                        print_message("\n👋 Goodbye!", "yellow")
                        break
                    except Exception as e:
                        print_message(f"❌ Input error: {e}", "red")
                        
        except KeyboardInterrupt:
            print_message("\n👋 Goodbye!", "yellow")
        except Exception as e:
            print_message(f"❌ Failed to initialize: {e}", "red")
            sys.exit(1)
    
    asyncio.run(run_chat())


@app.command()
def analyze(
    text: str = typer.Argument(..., help="Japanese text to analyze")
):
    """Analyze Japanese text."""
    
    async def run_analysis():
        agent = AIAgent()
        
        try:
            print_message("🔍 Analyzing Japanese text...", "blue")
            await agent.initialize()
            
            analysis = await agent.analyze_japanese_text(text)
            
            print_panel(f"Original Text: {analysis['original_text']}", "Analysis Results", "green")
            
            # Display tokens
            if analysis['tokens']:
                tokens_info = "\n".join([
                    f"• {token['surface']} ({token['pos']}) - {token.get('base_form', 'N/A')}"
                    for token in analysis['tokens'][:10]  # Show first 10 tokens
                ])
                if len(analysis['tokens']) > 10:
                    tokens_info += f"\n... and {len(analysis['tokens']) - 10} more tokens"
                print_panel(tokens_info, "Tokens", "cyan")
            
            # Display difficulty and kanji info
            info = f"Difficulty Level: {analysis['difficulty_level']}\n"
            info += f"Kanji Count: {len(analysis['kanji_info'])}\n"
            info += f"Grammar Patterns: {', '.join(analysis['grammar_patterns']) if analysis['grammar_patterns'] else 'None detected'}"
            print_panel(info, "Summary", "yellow")
            
        except Exception as e:
            print_message(f"❌ Analysis failed: {e}", "red")
            sys.exit(1)
    
    asyncio.run(run_analysis())


@app.command()
def translate(
    text: str = typer.Argument(..., help="Text to translate"),
    target: str = typer.Option("en", "--target", "-t", help="Target language (en, ja, etc.)")
):
    """Translate text to target language."""
    
    async def run_translation():
        agent = AIAgent()
        
        try:
            print_message("🌐 Translating text...", "blue")
            await agent.initialize()
            
            translation = await agent.translate_text(text, target)
            
            print_panel(f"Original ({target == 'ja' and 'en' or 'ja'}): {text}", "Translation", "green")
            print_panel(f"Translated ({target}): {translation}", "Result", "blue")
            
        except Exception as e:
            print_message(f"❌ Translation failed: {e}", "red")
            sys.exit(1)
    
    asyncio.run(run_translation())


@app.command()
def explain(
    text: str = typer.Argument(..., help="Japanese text to explain")
):
    """Explain Japanese grammar."""
    
    async def run_explanation():
        agent = AIAgent()
        
        try:
            print_message("📚 Explaining grammar...", "blue")
            await agent.initialize()
            
            explanation = await agent.explain_grammar(text)
            
            print_panel(f"Text: {text}", "Grammar Explanation", "green")
            print_panel(explanation, "Explanation", "blue")
            
        except Exception as e:
            print_message(f"❌ Explanation failed: {e}", "red")
            sys.exit(1)
    
    asyncio.run(run_explanation())


@app.command()
def server(
    host: str = typer.Option(settings.api_host, "--host", help="Host to bind to"),
    port: int = typer.Option(settings.api_port, "--port", help="Port to bind to"),
    reload: bool = typer.Option(settings.debug, "--reload/--no-reload", help="Enable auto-reload")
):
    """Start the API server."""
    try:
        import uvicorn
        print_message(f"🚀 Starting API server on {host}:{port}", "green")
        uvicorn.run(
            "ai_nihongo.api.main:app",
            host=host,
            port=port,
            reload=reload
        )
    except ImportError:
        print_message("❌ uvicorn not installed. Install with: pip install uvicorn", "red")
        sys.exit(1)


@app.command()
def config():
    """Show current configuration."""
    config_info = f"""
API Configuration:
- Host: {settings.api_host}
- Port: {settings.api_port}
- Debug: {settings.debug}

Model Configuration:
- Default Model: {settings.default_model}
- Max Tokens: {settings.max_tokens}
- Temperature: {settings.temperature}

Japanese Processing:
- Tokenizer: {settings.tokenizer_model}
- Sudachi Dict: {settings.sudachi_dict_type}

Database:
- Database URL: {settings.database_url}
- Redis URL: {settings.redis_url}

Logging:
- Log Level: {settings.log_level}
- Log File: {settings.log_file}
    """
    print_panel(config_info.strip(), "Configuration", "cyan")


def main():
    """Main entry point."""
    if not TYPER_AVAILABLE:
        print("CLI functionality requires 'typer' and 'rich' packages.")
        print("Install them with: pip install typer rich")
        print("\nFor basic usage, you can use the Python API directly:")
        print("  python -c \"import asyncio; from ai_nihongo import AIAgent; asyncio.run(AIAgent().initialize())\"")
        sys.exit(1)
    
    app()


if __name__ == "__main__":
    main()