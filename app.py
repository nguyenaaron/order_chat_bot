from flask import Flask, request, jsonify
from firebase_logic import store_message, get_messages
from openai_logic import generate_ai_reply
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/sms", methods=["POST"])
def sms_receive():
    incoming_msg = request.form.get("Body", "").strip()
    from_number = request.form.get("From", "").strip()

    # Store the incoming message as 'received'
    store_message(from_number, incoming_msg, direction="received")

    # Generate AI reply
    ai_reply = generate_ai_reply(incoming_msg)

    # Store the AI reply as 'sent'
    store_message(from_number, ai_reply, direction="sent")

    return jsonify({"reply": ai_reply}), 200

@app.route("/messages", methods=["GET"])
def view_messages():
    phone_number = request.args.get("phone")
    if not phone_number:
        return jsonify({"error": "Missing phone number query parameter."}), 400
    messages = get_messages(phone_number)
    # Convert timestamp to string for JSON serialization
    for msg in messages:
        if msg.get("timestamp"):
            msg["timestamp"] = str(msg["timestamp"])
    return jsonify({"messages": messages}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)