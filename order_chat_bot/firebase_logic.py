import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase only once
if not firebase_admin._apps:
    firebase_json_path = os.path.join(os.path.dirname(__file__), "firebase.json")
    cred = credentials.Certificate(firebase_json_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Store a message for a phone number
# direction: 'sent' (from system) or 'received' (from user)
def store_message(phone_number, text, direction):
    message_data = {
        'direction': direction,  # 'sent' or 'received'
        'text': text,
        'timestamp': firestore.SERVER_TIMESTAMP
    }
    db.collection('conversations').document(phone_number).collection('messages').add(message_data)

# Retrieve all messages for a phone number, ordered by timestamp
def get_messages(phone_number):
    messages_ref = db.collection('conversations').document(phone_number).collection('messages')
    query = messages_ref.order_by('timestamp')
    docs = query.stream()
    messages = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        messages.append(data)
    return messages

# Example usage
def print_conversation(phone_number):
    messages = get_messages(phone_number)
    for msg in messages:
        ts = msg['timestamp'].isoformat() if msg['timestamp'] else 'unknown time'
        print(f"[{ts}] {msg['direction']}: {msg['text']}")

def clear_conversation(phone_number):
    """Delete all stored messages for the given phone number"""
    conv_ref = db.collection('conversations').document(phone_number).collection('messages')
    for doc in conv_ref.stream():
        doc.reference.delete()

if __name__ == "__main__":
    # Example: store and print conversation for a phone number
    test_number = "+1234567890"
    store_message(test_number, "Hi, I want to order fish.", "received")
    store_message(test_number, "Sure! What type of fish and quantity?", "sent")
    print_conversation(test_number)
