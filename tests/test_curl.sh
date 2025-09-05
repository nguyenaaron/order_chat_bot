#!/bin/bash

# Quick Twilio SMS simulation using curl
# Make sure your Flask app is running first!

echo "🚀 Testing Twilio SMS webhook locally"
echo "====================================="

# Test 1: Simple hello message
echo -e "\n📱 Test 1: Hello message"
curl -X POST http://localhost:5001/sms \
  -d "Body=Hello there!" \
  -d "From=+15551234567" \
  -d "To=+15559876543" \
  -d "MessageSid=SM123456789" \
  -d "AccountSid=AC_TEST_ACCOUNT_SID_FOR_LOCAL_TESTING_ONLY"

echo -e "\n\n📱 Test 2: Order request"
curl -X POST http://localhost:5001/sms \
  -d "Body=I'd like to order a pizza" \
  -d "From=+15551234567" \
  -d "To=+15559876543" \
  -d "MessageSid=SM123456790" \
  -d "AccountSid=AC_TEST_ACCOUNT_SID_FOR_LOCAL_TESTING_ONLY"

echo -e "\n\n📱 Test 3: Menu question"
curl -X POST http://localhost:5001/sms \
  -d "Body=What's on the menu today?" \
  -d "From=+15551234567" \
  -d "To=+15559876543" \
  -d "MessageSid=SM123456791" \
  -d "AccountSid=AC_TEST_ACCOUNT_SID_FOR_LOCAL_TESTING_ONLY"

echo -e "\n\n✅ Tests completed!"
echo "💡 Check your Flask app console for the responses"
