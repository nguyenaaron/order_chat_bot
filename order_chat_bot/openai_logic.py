import os
import openai
from dotenv import load_dotenv
import json
import re

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_ai_reply(user_message, conversation_history=None):
    system_prompt = """
    You are a helpful person working at a seafood distribution company. You're friendly, casual, and genuinely want to help customers place their orders.
    
    Talk like a real person would - be natural, warm, and conversational. Don't sound like a customer service script.
    
    Your job:
    1. Chat naturally with customers - be friendly and personable
    2. Help them order fish: what they want, how much (in pounds), when they need it, and where to deliver
    3. Answer questions about products, pricing, or delivery in a helpful way
    4. Get all the order details: items with quantities in lbs, delivery date, and full delivery address
    
    How to talk:
    - Sound like you're having a normal conversation with someone
    - Use casual language: "Hey there!", "What can I get for you?", "Sure thing!", "No problem!"
    - Don't say "seafood items" - just say "What do you need?" or "What can I get you?"
    - Don't use formal phrases like "I can assist you" or "How may I help you today?"
    - Be genuinely helpful and interested, like you actually care about getting them what they need
    - Keep it short and natural - don't over-explain things
    - When asking for address, just say "What's the delivery address?" or "Where should I send it?"
    - Don't use flowery language like "delicious salmon" - just be direct and natural
    
    When someone greets you, respond like a real person: "Hey! What can I get for you today?" or "Hi there! What do you need?"
    
    For orders, just naturally ask:
    - What they want and how much (in pounds)
    - When they need it delivered  
    - Where to send it - just ask "What's the delivery address?" (include street and city)
    
    Be human, be helpful, be real.
    """
    
    # Build messages array with conversation history
    messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_history:
        # Add conversation history
        for msg in conversation_history:
            if msg["direction"] == "received":
                messages.append({"role": "user", "content": msg["text"]})
            else:
                messages.append({"role": "assistant", "content": msg["text"]})
    else:
        # Just add the current message if no history
        messages.append({"role": "user", "content": user_message})
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    ai_reply = response.choices[0].message.content.strip()
    return ai_reply


def parse_order_from_conversation(conversation):
    # Build a conversation string for the prompt (customer messages only)
    convo_str = ""
    for msg in conversation:
        if msg["direction"] == "received":
            convo_str += f"Customer: {msg['text']}\n"

    # Get current date info for intelligent year handling
    from datetime import datetime, timezone
    current_date = datetime.now(timezone.utc)
    current_year = current_date.year
    next_year = current_year + 1
    current_month = current_date.month
    current_day = current_date.day

    prompt = (
        "Given the following conversation between a customer and an assistant at a seafood distributor, "
        "extract the order details as JSON with these fields: items (list of {product, quantity}), delivery_date, delivery_address, and any notes. "
        "\nIMPORTANT REQUIREMENTS:"
        "\n1. All quantities MUST be in pounds (lbs). If no unit is specified, assume pounds."
        f"\n2. For dates: TODAY IS {current_date.strftime('%B %d, %Y')} (Month {current_month}, Day {current_day}, Year {current_year})"
        f"\n   CRITICAL: When someone says a partial date like 'July 25', you must determine the correct year:"
        f"\n   - If the month is AFTER the current month ({current_month}), use THIS YEAR ({current_year})"
        f"\n   - If the month is BEFORE the current month ({current_month}), use NEXT YEAR ({next_year})"
        f"\n   - If the month is THE SAME as current month ({current_month}):"
        f"\n     * If the day is >= current day ({current_day}), use THIS YEAR ({current_year})"
        f"\n     * If the day is < current day ({current_day}), use NEXT YEAR ({next_year})"
        f"\n   EXAMPLE: Today is {current_date.strftime('%B %d, %Y')}, so 'July 25' = July 25, {current_year if current_month < 7 or (current_month == 7 and current_day <= 25) else next_year}"
        "\n3. Delivery address: Extract complete addresses with street address and city. Accept any format that includes a street address and city name."
        "\n4. If someone provides a street address and city, that's sufficient - business name is optional."
        "\n5. Only mark delivery_address as null if NO address information is provided at all."
        "\n6. ASSUME ALL ADDRESSES ARE IN WASHINGTON STATE: If no state is mentioned, automatically add 'WA' to the address."
        "\n7. IMPORTANT: Always include a city name. If only a street address is given, you must infer or ask for the city."
        "\n\nExample format:"
        f'\n{{"items": [{{"product": "salmon", "quantity": "10 lbs"}}], "delivery_date": "Friday, July 25, {current_year if current_month < 7 or (current_month == 7 and current_day <= 25) else next_year}", "delivery_address": "123 Main St, Seattle, WA", "notes": "Before noon"}}'
        f"\n\nConversation:\n{convo_str}\n"
        "Order JSON:"
    )

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are an expert at extracting structured order data. Your most important task is to correctly determine the year for delivery dates. Today is {current_date.strftime('%B %d, %Y')}. If a customer provides a month and day that has already passed this year, you must use the next year. Otherwise, use the current year. Ensure all quantities are in pounds and all addresses are in Washington state."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    # Try to extract JSON from the response
    match = re.search(r'({.*})', content, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    else:
        return None


def is_order_complete(order_details):
    """Check if order has all required fields: items, delivery_date, delivery_address (with city)"""
    if not order_details:
        return False
    
    has_items = order_details.get('items') and len(order_details.get('items', [])) > 0
    
    # Safely handle delivery_date
    delivery_date = order_details.get('delivery_date')
    has_date = delivery_date and str(delivery_date).strip()
    
    # Check if address is complete (has city and street address)
    delivery_address = order_details.get('delivery_address')
    has_complete_address = False
    
    if delivery_address and str(delivery_address).strip():
        address = str(delivery_address).strip()
        address_lower = address.lower()
        
        # Look for patterns that indicate a complete address with city
        has_comma = ',' in address  # Most complete addresses have commas separating components
        has_multiple_parts = len(address.split()) >= 3  # Should have street number, street name, city
        
        # Check that it has at least 2 parts separated by commas (street, city)
        address_parts = address.split(',')
        has_street_and_city = len(address_parts) >= 2
        
        # Check that the first part (street address) has some substance
        if address_parts:
            first_part = address_parts[0].strip()
            has_valid_street = (
                len(first_part) > 5 and  # At least 6 characters for a street address
                any(char.isdigit() for char in first_part)  # Should have a street number
            )
            
            # Check that there's actually a city name (not just "WA")
            if len(address_parts) >= 2:
                second_part = address_parts[1].strip().lower()
                # Second part should be a city name, not just state abbreviation
                has_valid_city = (
                    len(second_part) > 2 and  # More than just "wa"
                    second_part not in ['wa'] and  # Not just the state abbreviation
                    any(char.isalpha() for char in second_part)  # Has letters (city name)
                )
            else:
                has_valid_city = False
        else:
            has_valid_street = False
            has_valid_city = False
        
        # Address is complete if it has street and actual city name
        has_complete_address = (
            has_comma and 
            has_multiple_parts and 
            has_street_and_city and
            has_valid_street and
            has_valid_city
        )
    
    return has_items and has_date and has_complete_address


def generate_order_confirmation_message(order_details, customer_phone):
    """Generate a confirmation message showing all order details"""
    if not order_details:
        return "I couldn't find any order details in our conversation."
    
    # Format items with bullet points
    items_text = ""
    for item in order_details.get('items', []):
        items_text += f"• {item.get('quantity', '')} {item.get('product', '')}\n"
    items_text = items_text.strip()
    
    confirmation_lines = [
        "Got it! Here's the order I have:",
        items_text,
        f"• Delivery date: {order_details.get('delivery_date', 'Not specified')}",
        f"• Address: {order_details.get('delivery_address', 'Not specified')}"
    ]
    
    # Add notes only if they exist
    notes = order_details.get('notes')
    if notes and notes.lower() not in ['none', 'n/a', '']:
        confirmation_lines.append(f"• Notes: {notes}")
    
    confirmation_lines.append("\nIf everything looks good, reply CONFIRM and I'll lock it in. If something's off, just let me know!")
    
    confirmation_msg = "\n".join(confirmation_lines)

    return confirmation_msg


def check_for_confirmation(message):
    """Check if the message is a confirmation (case-insensitive)"""
    return message.strip().upper() == "CONFIRM" 