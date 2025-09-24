"""Demo script showcasing AI-Nihongo functionality."""

import asyncio
from ai_nihongo.core.agent import AIAgent


async def demo():
    """Demonstrate AI-Nihongo capabilities."""
    
    print("🎌 AI-Nihongo Demo")
    print("=" * 50)
    
    # Initialize agent
    agent = AIAgent()
    await agent.initialize()
    
    # Demo Japanese texts
    texts = [
        "こんにちは",        # Hello (simple)
        "私は学生です",      # I am a student (basic)
        "本を読んでいます",   # I am reading a book (intermediate)
        "日本語を勉強しています"  # I am studying Japanese (intermediate)
    ]
    
    for i, text in enumerate(texts, 1):
        print(f"\n📝 Example {i}: {text}")
        print("-" * 30)
        
        try:
            # Analyze the text
            analysis = await agent.analyze_japanese_text(text)
            
            print(f"Difficulty: {analysis['difficulty_level']}")
            print(f"Tokens: {len(analysis['tokens'])}")
            print(f"Kanji: {len(analysis['kanji_info'])}")
            
            # Show first few tokens
            for token in analysis['tokens'][:3]:
                print(f"  • {token['surface']} ({token['pos']})")
            
            if len(analysis['tokens']) > 3:
                print(f"  ... and {len(analysis['tokens']) - 3} more tokens")
                
        except Exception as e:
            print(f"Error analyzing text: {e}")
    
    print(f"\n✅ Demo completed!")
    print("\n🚀 Try these commands:")
    print("  ai-nihongo analyze \"好きな食べ物は何ですか？\"")
    print("  ai-nihongo config")
    print("  ai-nihongo --help")


if __name__ == "__main__":
    asyncio.run(demo())