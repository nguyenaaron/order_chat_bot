#!/usr/bin/env python3
"""
Clear All Conversation History from Firebase
Use this to completely reset all stored conversations
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore

def clear_all_conversations():
    # Initialize Firebase if not already done
    if not firebase_admin._apps:
        firebase_json_path = os.path.join(os.path.dirname(__file__), "firebase.json")
        cred = credentials.Certificate(firebase_json_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    # Get all conversation documents
    conversations_ref = db.collection('conversations')
    conversations = conversations_ref.stream()
    
    deleted_count = 0
    
    for conversation in conversations:
        phone_number = conversation.id
        print(f"Deleting conversation for: {phone_number}")
        
        # Delete all messages in this conversation
        messages_ref = conversation.reference.collection('messages')
        messages = messages_ref.stream()
        
        for message in messages:
            message.reference.delete()
        
        # Delete the conversation document itself
        conversation.reference.delete()
        deleted_count += 1
    
    print(f"\n✅ Cleared {deleted_count} conversation(s) from Firebase")

if __name__ == "__main__":
    print("🗑️  Clearing all conversation history from Firebase...")
    clear_all_conversations()
    print("Done!") 