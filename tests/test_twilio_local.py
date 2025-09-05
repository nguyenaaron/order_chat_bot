#!/usr/bin/env python3
"""
Local Twilio SMS simulation script
This script simulates inbound SMS messages from Twilio to test your webhook locally
"""

import requests
import json
import os
from datetime import datetime

# Configuration
FLASK_URL = "http://localhost:5001/sms"
TEST_PHONE_NUMBER = "+15551234567"  # Change this to any test number you want

def simulate_sms(message_body):
    """
    Simulate an inbound SMS from Twilio
    """
    # Twilio sends these exact form fields
    twilio_data = {
        "Body": message_body,
        "From": TEST_PHONE_NUMBER,
        "To": "+15559876543",  # Your Twilio number
        "MessageSid": f"SM{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "AccountSid": "AC_TEST_ACCOUNT_SID_FOR_LOCAL_TESTING_ONLY",
        "FromCity": "San Francisco",
        "FromState": "CA",
        "FromCountry": "US",
        "ToCity": "New York",
        "ToState": "NY",
        "ToCountry": "US",
        "FromZip": "94105",
        "ToZip": "10001",
        "NumMedia": "0"
    }
    
    print(f"📱 Simulating SMS from {TEST_PHONE_NUMBER}")
    print(f"💬 Message: {message_body}")
    print(f"🌐 Sending to: {FLASK_URL}")
    
    try:
        response = requests.post(FLASK_URL, data=twilio_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! AI Reply: {result.get('reply', 'No reply')}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure your Flask app is running on port 5001")
        print("💡 Run: python app.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def interactive_mode():
    """
    Run in interactive mode to send multiple messages
    """
    print("🚀 Twilio SMS Simulator - Interactive Mode")
    print("=" * 50)
    print(f"📞 Test phone number: {TEST_PHONE_NUMBER}")
    print("💡 Type 'quit' to exit, 'help' for commands")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n💬 Enter message to simulate: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("📚 Available commands:")
                print("  - Type any message to simulate an SMS")
                print("  - 'quit' to exit")
                print("  - 'help' to show this message")
                print("  - 'test' to send a test message")
            elif user_input.lower() == 'test':
                simulate_sms("Hello! This is a test message.")
            elif user_input:
                simulate_sms(user_input)
            else:
                print("⚠️  Please enter a message")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def test_scenarios():
    """
    Run through common test scenarios
    """
    test_messages = [
        "Hello",
        "I'd like to order a pizza",
        "What's on the menu?",
        "How much does delivery cost?",
        "Can I get a refund?",
        "What are your hours?",
        "Do you have vegetarian options?",
        "I have a food allergy, what should I do?"
    ]
    
    print("🧪 Running test scenarios...")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔬 Test {i}/{len(test_messages)}")
        simulate_sms(message)
        input("Press Enter to continue to next test...")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode
        message = " ".join(sys.argv[1:])
        simulate_sms(message)
    else:
        # Interactive mode
        print("Choose mode:")
        print("1. Interactive mode (recommended for testing)")
        print("2. Run test scenarios")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "2":
            test_scenarios()
        else:
            interactive_mode()
