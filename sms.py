from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/sms", methods=["POST"])
def sms_reply():
    # Twilio sends x-www-form-urlencoded data
    from_number = request.form.get("From")
    to_number = request.form.get("To")
    body = request.form.get("Body")
    message_sid = request.form.get("MessageSid")

    print(f"📩 Incoming SMS: {from_number} → {to_number}")
    print(f"Message SID: {message_sid}")
    print(f"Body: {body}")

    # Normally you'd parse + save to Google Sheet here
    reply_text = f"Got it! You ordered: {body}"

    # Twilio expects XML (TwiML), but for local dev JSON is fine
    return jsonify({"reply": reply_text, "sid": message_sid})

if __name__ == "__main__":
    app.run(port=3000, debug=True)
