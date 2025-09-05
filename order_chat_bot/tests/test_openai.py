from openai_logic import generate_ai_reply

def test_openai():
    # Test message
    test_message = "Hello, I would like to order some fish."
    
    print(f"Testing with message: '{test_message}'")
    print("-" * 50)
    
    try:
        # Generate AI reply
        ai_reply = generate_ai_reply(test_message)
        print(f"AI Reply: {ai_reply}")
        print("✅ OpenAI test successful!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_openai() 