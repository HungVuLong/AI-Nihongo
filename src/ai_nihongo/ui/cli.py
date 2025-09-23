"""
Command-line interface for AI-Nihongo application.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, TaskID
from typing import Dict, List, Any, Optional
import json
import time

from ..llm.client import llm_client
from ..practice.exercises import VocabularyPractice, GrammarPractice, ConversationPractice
from ..core.config import config


console = Console()


class JapaneseUI:
    """User interface for Japanese learning application."""
    
    def __init__(self):
        """Initialize the UI."""
        self.vocabulary_practice = VocabularyPractice()
        self.grammar_practice = GrammarPractice()
        self.conversation_practice = ConversationPractice()
        self.user_language = config.default_language
        self.difficulty = config.difficulty_level
    
    def show_welcome(self):
        """Display welcome message."""
        welcome_text = """
        Welcome to AI-Nihongo! 🇯🇵
        
        Your Vietnamese-Japanese-English AI Language Learning Assistant
        
        Features:
        • Vocabulary Practice with Flashcards
        • Grammar Exercises and Explanations  
        • Conversation Practice Scenarios
        • Multi-language Translation (VI/JA/EN)
        • AI-Powered Learning Assistance
        """
        
        console.print(Panel(welcome_text, title="AI-Nihongo", style="bold blue"))
    
    def show_main_menu(self) -> str:
        """Display main menu and get user choice."""
        console.print("\n[bold green]Main Menu[/bold green]")
        console.print("1. 📚 Vocabulary Practice")
        console.print("2. 📝 Grammar Exercises") 
        console.print("3. 💬 Conversation Practice")
        console.print("4. 🔄 Translation")
        console.print("5. ⚙️  Settings")
        console.print("6. ❌ Exit")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5", "6"])
        return choice
    
    def vocabulary_menu(self):
        """Handle vocabulary practice menu."""
        console.print("\n[bold cyan]📚 Vocabulary Practice[/bold cyan]")
        
        # Topic selection
        topics = self.vocabulary_practice.topics
        console.print("\nAvailable topics:")
        for i, topic in enumerate(topics, 1):
            console.print(f"{i}. {topic.replace('_', ' ').title()}")
        
        topic_choice = Prompt.ask(
            "Choose a topic",
            choices=[str(i) for i in range(1, len(topics) + 1)]
        )
        selected_topic = topics[int(topic_choice) - 1]
        
        # Number of words
        word_count = int(Prompt.ask("Number of words to practice", default="10"))
        
        console.print(f"\n[yellow]Loading vocabulary for {selected_topic}...[/yellow]")
        
        with Progress() as progress:
            task = progress.add_task("[green]Generating vocabulary...", total=100)
            
            vocabulary_set = self.vocabulary_practice.get_vocabulary_set(
                topic=selected_topic,
                difficulty=self.difficulty,
                count=word_count,
                language=self.user_language
            )
            
            progress.update(task, advance=100)
        
        # Practice mode selection
        console.print("\n[bold]Practice Modes:[/bold]")
        console.print("1. 📇 Flashcards")
        console.print("2. 🧩 Quiz")
        
        mode_choice = Prompt.ask("Choose practice mode", choices=["1", "2"])
        
        if mode_choice == "1":
            self.run_flashcards(vocabulary_set)
        else:
            self.run_vocabulary_quiz(vocabulary_set)
    
    def run_flashcards(self, vocabulary_set: List[Dict[str, Any]]):
        """Run flashcard practice session."""
        console.print("\n[bold blue]📇 Flashcard Practice[/bold blue]")
        console.print("Press Enter to see the answer, 'q' to quit\n")
        
        for i, vocab in enumerate(vocabulary_set, 1):
            console.print(f"\n[bold]Card {i}/{len(vocabulary_set)}[/bold]")
            
            if vocab.get("type") == "vocabulary":
                japanese_word = vocab.get("japanese", vocab.get("question", ""))
                console.print(Panel(f"[bold cyan]{japanese_word}[/bold cyan]", title="Japanese"))
                
                user_input = Prompt.ask("Press Enter for answer (or 'q' to quit)", default="")
                if user_input.lower() == 'q':
                    break
                
                # Show answer
                answer = vocab.get("correct_answer", "")
                vietnamese = vocab.get("vietnamese", "")
                hiragana = vocab.get("hiragana", "")
                explanation = vocab.get("explanation", "")
                
                answer_text = f"[bold green]English:[/bold green] {answer}\n"
                if vietnamese:
                    answer_text += f"[bold yellow]Vietnamese:[/bold yellow] {vietnamese}\n"
                if hiragana and hiragana != japanese_word:
                    answer_text += f"[bold magenta]Hiragana:[/bold magenta] {hiragana}\n"
                if explanation:
                    answer_text += f"[italic]{explanation}[/italic]"
                
                console.print(Panel(answer_text, title="Answer"))
            else:
                # Handle other question types
                console.print(Panel(vocab.get("question", ""), title="Question"))
                user_input = Prompt.ask("Press Enter for answer (or 'q' to quit)", default="")
                if user_input.lower() == 'q':
                    break
                
                answer_text = vocab.get("correct_answer", "")
                explanation = vocab.get("explanation", "")
                if explanation:
                    answer_text += f"\n\n[italic]{explanation}[/italic]"
                
                console.print(Panel(answer_text, title="Answer"))
        
        console.print("\n[bold green]Flashcard session completed! 🎉[/bold green]")
    
    def run_vocabulary_quiz(self, vocabulary_set: List[Dict[str, Any]]):
        """Run vocabulary quiz."""
        console.print("\n[bold blue]🧩 Vocabulary Quiz[/bold blue]")
        
        quiz_questions = self.vocabulary_practice.quiz_vocabulary(vocabulary_set)
        score = 0
        
        for i, question in enumerate(quiz_questions, 1):
            console.print(f"\n[bold]Question {i}/{len(quiz_questions)}[/bold]")
            console.print(question["question"])
            
            if question.get("options"):
                for j, option in enumerate(question["options"], 1):
                    console.print(f"{j}. {option}")
                user_answer = Prompt.ask("Your answer", choices=[str(j) for j in range(1, len(question["options"]) + 1)])
                user_answer = question["options"][int(user_answer) - 1]
            else:
                user_answer = Prompt.ask("Your answer")
            
            correct_answer = question["correct_answer"]
            if user_answer.lower().strip() == correct_answer.lower().strip():
                console.print("[bold green]✓ Correct![/bold green]")
                score += 1
            else:
                console.print(f"[bold red]✗ Incorrect. Correct answer: {correct_answer}[/bold red]")
            
            if question.get("explanation"):
                console.print(f"[italic]{question['explanation']}[/italic]")
        
        # Show final score
        percentage = (score / len(quiz_questions)) * 100
        console.print(f"\n[bold]Final Score: {score}/{len(quiz_questions)} ({percentage:.1f}%)[/bold]")
        
        if percentage >= 80:
            console.print("[bold green]Excellent work! 🌟[/bold green]")
        elif percentage >= 60:
            console.print("[bold yellow]Good job! Keep practicing! 👍[/bold yellow]")
        else:
            console.print("[bold red]Keep studying! You'll improve! 💪[/bold red]")
    
    def grammar_menu(self):
        """Handle grammar practice menu."""
        console.print("\n[bold cyan]📝 Grammar Exercises[/bold cyan]")
        
        # Grammar point selection
        grammar_points = self.grammar_practice.grammar_points
        console.print("\nAvailable grammar points:")
        for i, point in enumerate(grammar_points, 1):
            console.print(f"{i}. {point.replace('_', ' ').title()}")
        
        point_choice = Prompt.ask(
            "Choose a grammar point",
            choices=[str(i) for i in range(1, len(grammar_points) + 1)]
        )
        selected_point = grammar_points[int(point_choice) - 1]
        
        console.print(f"\n[yellow]Loading grammar exercises for {selected_point}...[/yellow]")
        
        exercises = self.grammar_practice.get_grammar_exercises(
            grammar_point=selected_point,
            difficulty=self.difficulty,
            language=self.user_language
        )
        
        self.run_grammar_exercises(exercises)
    
    def run_grammar_exercises(self, exercises: List[Dict[str, Any]]):
        """Run grammar practice exercises."""
        console.print("\n[bold blue]📝 Grammar Practice[/bold blue]")
        
        score = 0
        for i, exercise in enumerate(exercises, 1):
            console.print(f"\n[bold]Exercise {i}/{len(exercises)}[/bold]")
            console.print(exercise["question"])
            
            if exercise.get("options"):
                for j, option in enumerate(exercise["options"], 1):
                    console.print(f"{j}. {option}")
                user_answer = Prompt.ask("Your answer", choices=[str(j) for j in range(1, len(exercise["options"]) + 1)])
                user_answer = exercise["options"][int(user_answer) - 1]
            else:
                user_answer = Prompt.ask("Your answer")
            
            correct_answer = exercise["correct_answer"]
            if user_answer.lower().strip() == correct_answer.lower().strip():
                console.print("[bold green]✓ Correct![/bold green]")
                score += 1
            else:
                console.print(f"[bold red]✗ Incorrect. Correct answer: {correct_answer}[/bold red]")
            
            if exercise.get("explanation"):
                console.print(f"[italic]{exercise['explanation']}[/italic]")
        
        # Show final score
        percentage = (score / len(exercises)) * 100
        console.print(f"\n[bold]Final Score: {score}/{len(exercises)} ({percentage:.1f}%)[/bold]")
    
    def conversation_menu(self):
        """Handle conversation practice menu."""
        console.print("\n[bold cyan]💬 Conversation Practice[/bold cyan]")
        
        # Scenario selection
        scenarios = self.conversation_practice.scenarios
        console.print("\nAvailable scenarios:")
        for i, scenario in enumerate(scenarios, 1):
            console.print(f"{i}. {scenario.replace('_', ' ').title()}")
        
        scenario_choice = Prompt.ask(
            "Choose a scenario",
            choices=[str(i) for i in range(1, len(scenarios) + 1)]
        )
        selected_scenario = scenarios[int(scenario_choice) - 1]
        
        console.print(f"\n[yellow]Loading conversation scenario: {selected_scenario}...[/yellow]")
        
        scenario_data = self.conversation_practice.get_conversation_scenario(
            scenario=selected_scenario,
            difficulty=self.difficulty,
            language=self.user_language
        )
        
        self.run_conversation_practice(scenario_data)
    
    def run_conversation_practice(self, scenario: Dict[str, Any]):
        """Run conversation practice session."""
        console.print("\n[bold blue]💬 Conversation Practice[/bold blue]")
        console.print(f"[bold]Scenario:[/bold] {scenario.get('question', 'Conversation Practice')}")
        
        if scenario.get("dialogue"):
            console.print("\n[bold]Sample Dialogue:[/bold]")
            for line in scenario["dialogue"]:
                speaker = line.get("speaker", "Speaker")
                japanese = line.get("japanese", "")
                english = line.get("english", "")
                vietnamese = line.get("vietnamese", "")
                
                console.print(f"\n[bold cyan]{speaker}:[/bold cyan] {japanese}")
                console.print(f"[dim]English:[/dim] {english}")
                if vietnamese:
                    console.print(f"[dim]Vietnamese:[/dim] {vietnamese}")
        else:
            console.print(f"\n{scenario.get('correct_answer', scenario.get('explanation', 'Practice conversation'))}")
        
        console.print(f"\n[italic]{scenario.get('explanation', '')}[/italic]")
        
        # Interactive practice
        if Confirm.ask("\nWould you like to practice this conversation?"):
            console.print("\n[yellow]Practice mode: Try to say the Japanese phrases![/yellow]")
            console.print("Press Enter after each attempt to continue...")
            
            if scenario.get("dialogue"):
                for line in scenario["dialogue"]:
                    speaker = line.get("speaker", "Speaker")
                    japanese = line.get("japanese", "")
                    english = line.get("english", "")
                    
                    console.print(f"\n[bold]Your turn to say ({speaker}):[/bold]")
                    console.print(f"[dim]Hint (English):[/dim] {english}")
                    
                    user_input = Prompt.ask("Press Enter when ready to see the answer", default="")
                    console.print(f"[bold green]Japanese:[/bold green] {japanese}")
    
    def translation_menu(self):
        """Handle translation feature."""
        console.print("\n[bold cyan]🔄 Translation[/bold cyan]")
        
        # Language selection
        languages = {"1": "en", "2": "vi", "3": "ja"}
        console.print("\nLanguages:")
        console.print("1. English")
        console.print("2. Vietnamese")
        console.print("3. Japanese")
        
        source_choice = Prompt.ask("Source language", choices=["1", "2", "3"])
        target_choice = Prompt.ask("Target language", choices=["1", "2", "3"])
        
        source_lang = languages[source_choice]
        target_lang = languages[target_choice]
        
        if source_lang == target_lang:
            console.print("[bold red]Source and target languages cannot be the same![/bold red]")
            return
        
        text_to_translate = Prompt.ask("Enter text to translate")
        
        console.print(f"\n[yellow]Translating...[/yellow]")
        
        try:
            translation = llm_client.translate_text(
                text=text_to_translate,
                source_lang=source_lang,
                target_lang=target_lang
            )
            
            console.print(Panel(translation, title="Translation", style="bold green"))
            
            # If translating to/from Japanese, offer grammar explanation
            if target_lang == "ja" or source_lang == "ja":
                if Confirm.ask("Would you like a grammar explanation?"):
                    japanese_text = translation if target_lang == "ja" else text_to_translate
                    explanation = llm_client.explain_japanese_grammar(japanese_text, self.user_language)
                    console.print(Panel(explanation, title="Grammar Explanation", style="bold blue"))
                    
        except Exception as e:
            console.print(f"[bold red]Translation failed: {str(e)}[/bold red]")
    
    def settings_menu(self):
        """Handle settings menu."""
        console.print("\n[bold cyan]⚙️ Settings[/bold cyan]")
        
        console.print(f"Current Language: {self.user_language}")
        console.print(f"Current Difficulty: {self.difficulty}")
        
        console.print("\n1. Change Language")
        console.print("2. Change Difficulty") 
        console.print("3. Back to Main Menu")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3"])
        
        if choice == "1":
            lang_choices = {"1": "en", "2": "vi", "3": "ja"}
            console.print("\nLanguages:")
            console.print("1. English")
            console.print("2. Vietnamese") 
            console.print("3. Japanese")
            
            lang_choice = Prompt.ask("Choose language", choices=["1", "2", "3"])
            self.user_language = lang_choices[lang_choice]
            console.print(f"[bold green]Language changed to {self.user_language}[/bold green]")
            
        elif choice == "2":
            diff_choices = {"1": "beginner", "2": "intermediate", "3": "advanced"}
            console.print("\nDifficulty levels:")
            console.print("1. Beginner")
            console.print("2. Intermediate")
            console.print("3. Advanced")
            
            diff_choice = Prompt.ask("Choose difficulty", choices=["1", "2", "3"])
            self.difficulty = diff_choices[diff_choice]
            console.print(f"[bold green]Difficulty changed to {self.difficulty}[/bold green]")
    
    def run(self):
        """Run the main application loop."""
        self.show_welcome()
        
        while True:
            try:
                choice = self.show_main_menu()
                
                if choice == "1":
                    self.vocabulary_menu()
                elif choice == "2":
                    self.grammar_menu()
                elif choice == "3":
                    self.conversation_menu()
                elif choice == "4":
                    self.translation_menu()
                elif choice == "5":
                    self.settings_menu()
                elif choice == "6":
                    console.print("\n[bold green]Thanks for using AI-Nihongo! がんばって！ (Ganbatte!)[/bold green]")
                    break
                    
            except KeyboardInterrupt:
                console.print("\n\n[bold yellow]Goodbye! またね！ (Mata ne!)[/bold yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]An error occurred: {str(e)}[/bold red]")
                console.print("Please try again.")


def main():
    """Main entry point for the CLI application."""
    ui = JapaneseUI()
    ui.run()


if __name__ == "__main__":
    main()