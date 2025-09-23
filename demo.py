#!/usr/bin/env python3
"""
Demo script for AI-Nihongo application.
Shows basic functionality without requiring OpenAI API key.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_nihongo.practice.exercises import VocabularyPractice, GrammarPractice, ConversationPractice
from ai_nihongo.utils.helpers import create_sample_data

console = Console()


def demo_vocabulary():
    """Demonstrate vocabulary practice functionality."""
    console.print("\n[bold cyan]📚 Vocabulary Practice Demo[/bold cyan]")
    
    vocab_practice = VocabularyPractice()
    
    # Get sample vocabulary (uses fallback data)
    vocabulary_set = vocab_practice.get_vocabulary_set(
        topic="daily_life",
        difficulty="beginner",
        count=5
    )
    
    table = Table(title="Sample Vocabulary - Daily Life")
    table.add_column("Japanese", style="bold cyan")
    table.add_column("Hiragana", style="yellow")
    table.add_column("English", style="green")
    table.add_column("Vietnamese", style="magenta")
    
    for vocab in vocabulary_set:
        if vocab.get("type") == "vocabulary":
            table.add_row(
                vocab.get("japanese", ""),
                vocab.get("hiragana", ""),
                vocab.get("correct_answer", ""),
                vocab.get("vietnamese", "")
            )
    
    console.print(table)


def demo_grammar():
    """Demonstrate grammar practice functionality."""
    console.print("\n[bold cyan]📝 Grammar Practice Demo[/bold cyan]")
    
    grammar_practice = GrammarPractice()
    
    # Get sample grammar exercises
    exercises = grammar_practice.get_grammar_exercises(
        grammar_point="particles",
        difficulty="beginner",
        count=3
    )
    
    for i, exercise in enumerate(exercises, 1):
        console.print(f"\n[bold]Exercise {i}:[/bold]")
        console.print(f"Question: {exercise['question']}")
        console.print(f"Answer: {exercise['correct_answer']}")
        if exercise.get("explanation"):
            console.print(f"[italic]Explanation: {exercise['explanation']}[/italic]")


def demo_conversation():
    """Demonstrate conversation practice functionality."""
    console.print("\n[bold cyan]💬 Conversation Practice Demo[/bold cyan]")
    
    conversation_practice = ConversationPractice()
    
    # Get sample conversation
    scenario = conversation_practice.get_conversation_scenario(
        scenario="greeting",
        difficulty="beginner"
    )
    
    console.print(f"[bold]Scenario:[/bold] {scenario.get('question', 'Basic Greeting')}")
    
    if scenario.get("dialogue"):
        console.print("\n[bold]Sample Dialogue:[/bold]")
        for line in scenario["dialogue"]:
            speaker = line.get("speaker", "Speaker")
            japanese = line.get("japanese", "")
            english = line.get("english", "")
            vietnamese = line.get("vietnamese", "")
            
            console.print(f"\n[bold cyan]{speaker}:[/bold cyan] {japanese}")
            console.print(f"  [dim]English:[/dim] {english}")
            if vietnamese:
                console.print(f"  [dim]Vietnamese:[/dim] {vietnamese}")


def demo_translation():
    """Demonstrate translation functionality (fallback mode)."""
    console.print("\n[bold cyan]🔄 Translation Demo[/bold cyan]")
    
    # Show sample translations (these would normally use LLM)
    translations = [
        {
            "original": "Hello, how are you?",
            "language": "English → Japanese",
            "translated": "こんにちは、元気ですか？"
        },
        {
            "original": "Xin chào, bạn khỏe không?",
            "language": "Vietnamese → Japanese", 
            "translated": "こんにちは、元気ですか？"
        },
        {
            "original": "ありがとうございます",
            "language": "Japanese → English",
            "translated": "Thank you very much"
        }
    ]
    
    table = Table(title="Sample Translations")
    table.add_column("Original", style="cyan")
    table.add_column("Language Pair", style="yellow")
    table.add_column("Translation", style="green")
    
    for trans in translations:
        table.add_row(trans["original"], trans["language"], trans["translated"])
    
    console.print(table)


def main():
    """Run the demo."""
    console.print(Panel(
        "[bold blue]AI-Nihongo Demo[/bold blue]\n\n" +
        "Vietnamese-Japanese-English AI Language Learning Application\n\n" +
        "[yellow]This demo shows the application's functionality using fallback data.\n" +
        "For full AI-powered features, configure an OpenAI API key.[/yellow]",
        title="Welcome to AI-Nihongo",
        style="bold blue"
    ))
    
    # Create sample data
    console.print("\n[yellow]Creating sample data...[/yellow]")
    create_sample_data()
    
    # Run demonstrations
    demo_vocabulary()
    demo_grammar()
    demo_conversation()
    demo_translation()
    
    console.print("\n" + "="*60)
    console.print(Panel(
        "[bold green]Demo completed![/bold green]\n\n" +
        "To try the full interactive application:\n" +
        "[cyan]python main.py[/cyan]\n\n" +
        "To configure AI features:\n" +
        "1. Copy .env.example to .env\n" +
        "2. Add your OpenAI API key\n" +
        "3. Run the application\n\n" +
        "[yellow]がんばって！ (Ganbatte! - Good luck!)[/yellow]",
        title="Next Steps",
        style="bold green"
    ))


if __name__ == "__main__":
    main()