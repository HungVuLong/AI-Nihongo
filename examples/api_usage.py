"""API usage example using requests."""

import requests
import json


def main():
    """Example of using the AI-Nihongo API."""
    
    base_url = "http://localhost:8000"
    
    print("🌐 AI-Nihongo API Example")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        print("Start the server with: ai-nihongo server")
        return
    
    # Example 1: Chat
    print("\n1. Chat Example:")
    chat_data = {
        "message": "こんにちは！",
        "user_id": "example_user"
    }
    
    response = requests.post(f"{base_url}/chat", json=chat_data)
    if response.status_code == 200:
        result = response.json()
        print(f"User: {chat_data['message']}")
        print(f"AI: {result['response']}")
    else:
        print(f"❌ Chat failed: {response.status_code}")
    
    # Example 2: Text Analysis
    print("\n2. Text Analysis Example:")
    analysis_data = {"text": "私は学生です。"}
    
    response = requests.post(f"{base_url}/analyze", json=analysis_data)
    if response.status_code == 200:
        result = response.json()
        print(f"Text: {result['original_text']}")
        print(f"Difficulty: {result['difficulty_level']}")
        print(f"Tokens: {len(result['tokens'])}")
    else:
        print(f"❌ Analysis failed: {response.status_code}")
    
    # Example 3: Translation
    print("\n3. Translation Example:")
    translation_data = {
        "text": "Hello, how are you?",
        "target_language": "ja"
    }
    
    response = requests.post(f"{base_url}/translate", json=translation_data)
    if response.status_code == 200:
        result = response.json()
        print(f"Original: {result['original_text']}")
        print(f"Translated: {result['translated_text']}")
    else:
        print(f"❌ Translation failed: {response.status_code}")
    
    # Example 4: Grammar Explanation
    print("\n4. Grammar Explanation Example:")
    grammar_data = {"text": "本を読んでいます。"}
    
    response = requests.post(f"{base_url}/explain-grammar", json=grammar_data)
    if response.status_code == 200:
        result = response.json()
        print(f"Text: {result['text']}")
        print(f"Explanation: {result['explanation']}")
    else:
        print(f"❌ Grammar explanation failed: {response.status_code}")
    
    print("\n✅ API examples completed!")


if __name__ == "__main__":
    main()