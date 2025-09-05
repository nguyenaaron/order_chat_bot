#!/usr/bin/env python3
"""
Clean SMS Chatbot Demo - No Debug Output
Interactive terminal demo for testing the SMS chatbot order flow
"""

import sys
from datetime import datetime
from firebase_logic import store_message, get_messages, clear_conversation
from openai_logic import generate_ai_reply, parse_order_from_conversation, is_order_complete, generate_order_confirmation_message, check_for_confirmation
from sheets_logic import process_confirmed_order

def print_separator():
    print("═" * 60)

def print_message(sender, message, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M")
    
    if sender == "You":
        print(f"[{timestamp}] 🧑 You: {message}")
    else:
        print(f"[{timestamp}] 🤖 Bot: {message}")

def main():
    print_separator()
    print("🐟 SEAFOOD DISTRIBUTION SMS CHATBOT - DEMO")
    print_separator()
    print("Welcome! This simulates SMS conversations with customers.")
    print("Type your messages as a customer would.")
    print("Commands: 'quit' to exit, 'reset' to start a new conversation")
    print_separator()
    
    # Use a demo phone number
    phone_number = "+1-555-DEMO"
    # Clear any existing history for this demo number
    clear_conversation(phone_number)
    
    conversation_state = "chatting"  # chatting, confirming, confirmed
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 Your message: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for testing the SMS chatbot!")
                break
            
            if user_input.lower() == 'reset':
                # Clear current conversation in Firebase
                clear_conversation(phone_number)
                
                # Generate a new phone number to start fresh
                import random
                phone_number = f"+1-555-DEMO{random.randint(100, 999)}"
                conversation_state = "chatting"
                print(f"\n🔄 Conversation reset! New session started.")
                print_separator()
                continue
            
            if not user_input:
                continue
            
            # Store the user message
            store_message(phone_number, user_input, "received")
            
            # Get conversation history
            conversation_history = get_messages(phone_number)
            
            # Check if this is a confirmation
            if conversation_state == "confirming" and check_for_confirmation(user_input):
                # Process the confirmed order
                order_details = parse_order_from_conversation(conversation_history)
                
                try:
                    process_confirmed_order(phone_number, order_details)
                    ai_response = "🎉 Perfect! Your order has been confirmed and added to our system. You'll receive a confirmation call within 24 hours. Thank you for your business!"
                    conversation_state = "confirmed"
                except Exception as e:
                    ai_response = "✅ Your order has been confirmed! However, there was a technical issue saving it to our spreadsheet. Don't worry - we have your order details and will process it manually."
                
                store_message(phone_number, ai_response, "sent")
                print_message("Bot", ai_response)
                
                # Auto-reset after order confirmation
                import random
                phone_number = f"+1-555-DEMO{random.randint(100, 999)}"
                conversation_state = "chatting"
                print(f"\n🔄 Ready for next customer! (Session auto-reset)")
                print_separator()
                continue
            
            # Generate AI response
            ai_response = generate_ai_reply(user_input, conversation_history)
            store_message(phone_number, ai_response, "sent")
            print_message("Bot", ai_response)
            
            # Check if we have a complete order to confirm
            if conversation_state == "chatting":
                order_details = parse_order_from_conversation(conversation_history)
                
                if order_details and is_order_complete(order_details):
                    # Generate confirmation message
                    confirmation_msg = generate_order_confirmation_message(order_details, phone_number)
                    store_message(phone_number, confirmation_msg, "sent")
                    
                    print("\n" + "─" * 60)
                    print_message("Bot", confirmation_msg)
                    print("─" * 60)
                    
                    conversation_state = "confirming"
        
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("The demo will continue...")

if __name__ == "__main__":
    main() 