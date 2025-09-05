from db import save_message, get_all_messages
from openai_logic import generate_ai_reply

def test_mongodb():
    print("Testing MongoDB connection and message saving...")
    print("-" * 50)
    
    try:
        # Test saving a message
        test_number = "+1234567890"
        test_message = "Hi, I need 10 pounds of salmon for tomorrow"
        
        print(f"Saving message from {test_number}: '{test_message}'")
        
        # Generate AI reply
        ai_reply = generate_ai_reply(test_message)
        print(f"AI Reply: {ai_reply}")
        
        # Save to MongoDB
        save_message(test_number, test_message, ai_reply)
        print("✅ Message saved to MongoDB!")
        
        # Retrieve all messages
        print("\nRetrieving all messages from MongoDB...")
        all_messages = get_all_messages()
        
        print(f"Found {len(all_messages)} messages:")
        for i, msg in enumerate(all_messages, 1):
            print(f"\nMessage {i}:")
            print(f"  From: {msg.get('from', 'N/A')}")
            print(f"  Message: {msg.get('message', 'N/A')}")
            print(f"  AI Reply: {msg.get('ai_reply', 'N/A')}")
            print(f"  ID: {msg.get('_id', 'N/A')}")
        
        print("\n✅ MongoDB test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mongodb() 