# Local Twilio SMS Testing Guide

This guide shows you how to test your Twilio SMS webhook locally without exposing your server to the internet.

## 🚀 Quick Start

### 1. Start Your Flask App
```bash
# Activate virtual environment
source venv/bin/activate

# Start the Flask app
python app.py
```

Your app will run on `http://localhost:5001`

### 2. Test with Python Script (Recommended)
```bash
# Interactive mode - best for development
python test_twilio_local.py

# Send a single message
python tests/test_twilio_local.py "Hello, I'd like to order a pizza"

# Run test scenarios
python tests/test_twilio_local.py
# Then choose option 2
```

### 3. Test with curl (Quick testing)
```bash
# Make the script executable first time
chmod +x test_curl.sh

# Run the test script
./test_curl.sh

# Or test manually with curl
curl -X POST http://localhost:5001/sms \
  -d "Body=Hello there!" \
  -d "From=+15551234567" \
  -d "To=+15559876543" \
  -d "MessageSid=SM123456789"
```

## 📱 What Gets Simulated

The test scripts send the exact same data format that Twilio sends:

- **Body**: The SMS message content
- **From**: The sender's phone number
- **To**: Your Twilio number
- **MessageSid**: Unique message identifier
- **AccountSid**: Your Twilio account ID
- **Location data**: City, state, country, zip code
- **Media info**: Number of media attachments

## 🔧 Customization

### Change Test Phone Number
Edit `test_twilio_local.py` and modify:
```python
TEST_PHONE_NUMBER = "+15551234567"  # Change this
```

### Test Different Scenarios
Add your own test messages in the `test_scenarios()` function:
```python
test_messages = [
    "Your custom message here",
    "Another test scenario",
    # ... more messages
]
```

## 🌐 For Production Testing

When you're ready to test with real Twilio:

1. **Use ngrok** to expose your local server:
   ```bash
   ngrok http 5001
   ```

2. **Update your Twilio webhook URL** to the ngrok URL:
   ```
   https://abc123.ngrok.io/sms
   ```

3. **Send real SMS** to your Twilio number

## 🐛 Troubleshooting

### Connection Failed
- Make sure your Flask app is running (`python app.py`)
- Check the port number (default: 5001)
- Verify the virtual environment is activated

### Import Errors
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're in the virtual environment

### Firebase/OpenAI Errors
- Check your `.env` file has the required API keys
- Verify your service account files are in place

## 📋 Test Scenarios Included

The test script includes common SMS scenarios:
- Greetings
- Order requests
- Menu questions
- Pricing inquiries
- Refund requests
- Hours questions
- Dietary restrictions
- Allergy concerns

## 🎯 Next Steps

1. Test basic functionality with the local simulator
2. Add your own test scenarios
3. Test with ngrok for real webhook testing
4. Deploy to production when ready

Happy testing! 🚀
