#!/usr/bin/env python3
"""
Terminal-based SMS Chatbot Demo
Simulates the full conversation flow without needing a real phone number
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebase_logic import store_message, get_messages
from openai_logic import (
    generate_ai_reply, 
    parse_order_from_conversation, 
    is_order_complete,
    generate_order_confirmation_message,
    check_for_confirmation
)

class SMSDemo:
    def __init__(self):
        self.phone_number = "+1555DEMO123"  # Fake phone number for demo
        self.conversation_history = []
        self.current_order = None
        self.awaiting_confirmation = False
        
    def start_demo(self):
        print("🐟 SMS Seafood Chatbot Demo")
        print("=" * 40)
        print(f"Demo phone number: {self.phone_number}")
        print("Type your messages as if you're texting the business.")
        print("Commands: 'quit', 'history', 'parse', 'order', 'reset'")
        print("-" * 40)
        
        while True:
            try:
                # Get user input
                user_message = input("\n📱 You: ").strip()
                
                if user_message.lower() == 'quit':
                    print("👋 Demo ended!")
                    break
                elif user_message.lower() == 'history':
                    self.show_conversation_history()
                    continue
                elif user_message.lower() == 'parse':
                    self.test_order_parsing()
                    continue
                elif user_message.lower() == 'order':
                    self.show_current_order()
                    continue
                elif user_message.lower() == 'reset':
                    self.reset_conversation()
                    continue
                elif not user_message:
                    continue
                
                # Check if user is confirming an order
                if self.awaiting_confirmation and check_for_confirmation(user_message):
                    self.process_order_confirmation()
                    self.awaiting_confirmation = False
                    continue
                
                # Store user message
                store_message(self.phone_number, user_message, "received")
                self.conversation_history.append({"direction": "received", "text": user_message})
                
                # Check if we should show order confirmation
                order_details = parse_order_from_conversation(self.conversation_history)
                if order_details and is_order_complete(order_details) and not self.awaiting_confirmation:
                    # Show confirmation instead of generating AI response
                    self.current_order = order_details
                    confirmation_msg = generate_order_confirmation_message(order_details, self.phone_number)
                    
                    store_message(self.phone_number, confirmation_msg, "sent")
                    self.conversation_history.append({"direction": "sent", "text": confirmation_msg})
                    
                    print(f"🤖 Business:\n{confirmation_msg}")
                    self.awaiting_confirmation = True
                else:
                    # Generate normal AI response
                    print("🤖 AI is thinking...")
                    ai_response = generate_ai_reply(user_message, self.conversation_history)
                    
                    # Store AI response
                    store_message(self.phone_number, ai_response, "sent")
                    self.conversation_history.append({"direction": "sent", "text": ai_response})
                    
                    print(f"🤖 Business: {ai_response}")
                
            except KeyboardInterrupt:
                print("\n👋 Demo ended!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
    
    def process_order_confirmation(self):
        """Process confirmed order and send to Google Sheets"""
        print("\n✅ ORDER CONFIRMED!")
        print("📤 Sending order to Google Sheets...")
        
        try:
            from sheets_logic import process_confirmed_order
            
            # Process the order using the sheets logic
            spreadsheet_id = process_confirmed_order(self.phone_number, self.current_order)
            
            print(f"📋 Order added to spreadsheet: {spreadsheet_id}")
            
            # Send confirmation message
            confirmation_response = "🎉 Thank you! Your order has been confirmed and added to our system. You'll receive updates on delivery status."
            store_message(self.phone_number, confirmation_response, "sent")
            self.conversation_history.append({"direction": "sent", "text": confirmation_response})
            print(f"🤖 Business: {confirmation_response}")
            
            # Reset order state
            self.current_order = None
            
        except Exception as e:
            error_msg = f"❌ Sorry, there was an error processing your order: {e}"
            print(error_msg)
            
            # Send error message to customer
            store_message(self.phone_number, error_msg, "sent")
            self.conversation_history.append({"direction": "sent", "text": error_msg})
            
            # Keep order state so customer can try again
            print("💡 Order state preserved - customer can try confirming again.")
    
    def show_conversation_history(self):
        print("\n📜 Conversation History:")
        print("-" * 30)
        if not self.conversation_history:
            print("No messages yet.")
            return
            
        for i, msg in enumerate(self.conversation_history, 1):
            who = "📱 You" if msg["direction"] == "received" else "🤖 Business"
            print(f"{i}. {who}: {msg['text'][:100]}{'...' if len(msg['text']) > 100 else ''}")
    
    def show_current_order(self):
        print("\n📋 Current Order Status:")
        print("-" * 30)
        
        if self.awaiting_confirmation and self.current_order:
            print("✅ Order ready for confirmation!")
            print(f"   Items: {self.current_order.get('items', 'None')}")
            print(f"   Delivery Date: {self.current_order.get('delivery_date', 'None')}")
            print(f"   Delivery Address: {self.current_order.get('delivery_address', 'None')}")
            print("   Type 'CONFIRM' to place the order.")
        else:
            order_details = parse_order_from_conversation(self.conversation_history)
            if order_details:
                print("📝 Partial order detected:")
                print(f"   Items: {order_details.get('items', 'None')}")
                print(f"   Delivery Date: {order_details.get('delivery_date', 'None')}")
                print(f"   Delivery Address: {order_details.get('delivery_address', 'None')}")
                if is_order_complete(order_details):
                    print("   ✅ Order is complete!")
                else:
                    print("   ⚠️  Order incomplete - missing some details.")
            else:
                print("No order detected in conversation yet.")
    
    def test_order_parsing(self):
        print("\n🔍 Testing Order Parsing...")
        print("-" * 30)
        
        if len(self.conversation_history) < 2:
            print("Not enough conversation history for order parsing.")
            return
        
        try:
            # Parse order from conversation
            order_details = parse_order_from_conversation(self.conversation_history)
            
            if order_details:
                print("✅ Parsed Order Details:")
                print(f"   Items: {order_details.get('items', 'None')}")
                print(f"   Delivery Date: {order_details.get('delivery_date', 'None')}")
                print(f"   Delivery Address: {order_details.get('delivery_address', 'None')}")
                print(f"   Notes: {order_details.get('notes', 'None')}")
                
                if is_order_complete(order_details):
                    print("🎉 Order is complete! Ready for confirmation.")
                else:
                    print("⚠️  Order incomplete - missing some details.")
            else:
                print("❌ Could not parse order from conversation.")
                
        except Exception as e:
            print(f"❌ Error parsing order: {e}")
    
    def reset_conversation(self):
        """Reset the conversation and order state"""
        self.conversation_history = []
        self.current_order = None
        self.awaiting_confirmation = False
        print("🔄 Conversation reset!")

def main():
    print("Starting SMS Chatbot Demo...")
    
    # Check if we can connect to services
    try:
        # Test OpenAI
        from openai_logic import generate_ai_reply
        print("✅ OpenAI connection ready")
        
        # Test Firebase (if available)
        try:
            from firebase_logic import store_message
            print("✅ Firebase connection ready")
        except Exception as e:
            print(f"⚠️  Firebase not available: {e}")
            print("   Demo will still work but won't persist messages.")
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return
    
    # Start demo
    demo = SMSDemo()
    demo.start_demo()

if __name__ == "__main__":
    main() 