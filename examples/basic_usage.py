"""Basic usage example for AI-Nihongo."""

import asyncio
from ai_nihongo import AIAgent


async def main():
    """Basic example of using AI-Nihongo."""
    
    # Create and initialize the agent
    agent = AIAgent()
    await agent.initialize()
    
    print("🤖 AI-Nihongo Example")
    print("=" * 50)
    
    # Example 1: Basic chat
    print("\n1. Basic Chat:")
    response = await agent.process_message("こんにちは！日本語を勉強しています。")
    print(f"AI: {response}")
    
    # Example 2: Text analysis
    print("\n2. Text Analysis:")
    text = "私は学生です。"
    analysis = await agent.analyze_japanese_text(text)
    print(f"Text: {text}")
    print(f"Difficulty: {analysis['difficulty_level']}")
    print(f"Tokens: {len(analysis['tokens'])}")
    
    # Example 3: Translation
    print("\n3. Translation:")
    original = "How are you?"
    translation = await agent.translate_text(original, "ja")
    print(f"English: {original}")
    print(f"Japanese: {translation}")
    
    # Example 4: Grammar explanation
    print("\n4. Grammar Explanation:")
    grammar_text = "本を読んでいます。"
    explanation = await agent.explain_grammar(grammar_text)
    print(f"Text: {grammar_text}")
    print(f"Explanation: {explanation}")
    
    print("\n✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(main())