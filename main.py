#!/usr/bin/env python3
"""
AI-Nihongo: Vietnamese-Japanese-English AI Language Learning Application

Main entry point for the application.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

import click
from rich.console import Console

from ai_nihongo.ui.cli import JapaneseUI, main as cli_main
from ai_nihongo.core.config import config
from ai_nihongo.utils.helpers import setup_logging, create_sample_data
from ai_nihongo import __version__, __description__

console = Console()


@click.command()
@click.version_option(version=__version__, prog_name="AI-Nihongo")
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--create-sample-data', is_flag=True, help='Create sample data files')
def main(debug, create_sample_data_flag):
    """
    AI-Nihongo: Vietnamese-Japanese-English AI Language Learning Application
    
    A comprehensive language learning tool powered by LLM technology for practicing Japanese
    with support for Vietnamese and English translations.
    """
    
    # Setup logging
    log_level = "DEBUG" if debug else config.log_level
    logger = setup_logging(log_level)
    
    try:
        # Create sample data if requested
        if create_sample_data_flag:
            console.print("[yellow]Creating sample data files...[/yellow]")
            sample_file = create_sample_data()
            console.print(f"[green]Sample data created: {sample_file}[/green]")
            return
        
        # Check if OpenAI API key is configured
        if not config.openai_api_key or config.openai_api_key == "your_openai_api_key_here":
            console.print("[bold red]Warning: OpenAI API key not configured![/bold red]")
            console.print("Please set your OpenAI API key in the .env file or environment variables.")
            console.print("The application will run with limited functionality using fallback data.")
            console.print()
        
        # Start the CLI application
        logger.info("Starting AI-Nihongo application")
        cli_main()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Application interrupted by user[/yellow]")
        logger.info("Application interrupted by user")
    except Exception as e:
        console.print(f"[bold red]Application error: {str(e)}[/bold red]")
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)


@click.group()
def cli():
    """AI-Nihongo command line tools."""
    pass


@cli.command()
def interactive():
    """Start interactive learning session."""
    ui = JapaneseUI()
    ui.run()


@cli.command()
@click.option('--text', required=True, help='Text to translate')
@click.option('--source', default='en', help='Source language (en/vi/ja)')
@click.option('--target', default='ja', help='Target language (en/vi/ja)')
def translate(text, source, target):
    """Quick translation command."""
    from ai_nihongo.llm.client import llm_client
    
    try:
        result = llm_client.translate_text(text, source, target)
        console.print(f"[bold green]Translation:[/bold green] {result}")
    except Exception as e:
        console.print(f"[bold red]Translation failed: {str(e)}[/bold red]")


@cli.command()
@click.option('--topic', default='daily_life', help='Vocabulary topic')
@click.option('--count', default=5, help='Number of words')
@click.option('--difficulty', default='beginner', help='Difficulty level')
def vocab(topic, count, difficulty):
    """Generate vocabulary practice set."""
    from ai_nihongo.practice.exercises import VocabularyPractice
    
    vocab_practice = VocabularyPractice()
    
    try:
        vocabulary_set = vocab_practice.get_vocabulary_set(
            topic=topic,
            difficulty=difficulty,
            count=count
        )
        
        console.print(f"[bold blue]Vocabulary: {topic} ({difficulty})[/bold blue]\n")
        
        for i, vocab in enumerate(vocabulary_set, 1):
            if vocab.get("type") == "vocabulary":
                japanese = vocab.get("japanese", "")
                english = vocab.get("correct_answer", "")
                vietnamese = vocab.get("vietnamese", "")
                console.print(f"{i}. [bold]{japanese}[/bold] - {english}")
                if vietnamese:
                    console.print(f"   Vietnamese: {vietnamese}")
            else:
                console.print(f"{i}. {vocab.get('question', '')}")
                console.print(f"   Answer: {vocab.get('correct_answer', '')}")
            console.print()
            
    except Exception as e:
        console.print(f"[bold red]Failed to generate vocabulary: {str(e)}[/bold red]")


@cli.command()
def demo():
    """Run a quick demo of the application features."""
    console.print(f"[bold blue]{__description__}[/bold blue]\n")
    
    # Demo translation
    console.print("[bold cyan]Demo: Translation[/bold cyan]")
    console.print("English: Hello, how are you?")
    console.print("Japanese: こんにちは、元気ですか？")
    console.print("Vietnamese: Xin chào, bạn khỏe không?\n")
    
    # Demo vocabulary
    console.print("[bold cyan]Demo: Vocabulary[/bold cyan]")
    sample_vocab = [
        {"japanese": "ありがとう", "english": "Thank you", "vietnamese": "Cảm ơn"},
        {"japanese": "すみません", "english": "Excuse me", "vietnamese": "Xin lỗi"},
        {"japanese": "はじめまして", "english": "Nice to meet you", "vietnamese": "Rất vui được gặp bạn"}
    ]
    
    for vocab in sample_vocab:
        console.print(f"• [bold]{vocab['japanese']}[/bold] - {vocab['english']} ({vocab['vietnamese']})")
    
    console.print(f"\n[green]Run 'python main.py' to start the full interactive application![/green]")


if __name__ == "__main__":
    # If run directly, start the main interactive application
    if len(sys.argv) == 1:
        main(debug=False, create_sample_data_flag=False)
    else:
        # Use click CLI for command-line options
        cli()