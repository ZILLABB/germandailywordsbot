#!/usr/bin/env python3
"""
Test script to verify Telegram bot connection.
Run this after setting up your BOT_TOKEN and CHAT_ID.
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_bot_connection():
    """Test the bot by sending a simple message."""
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    
    if not bot_token:
        print("❌ Error: BOT_TOKEN not found in environment variables.")
        return False
    
    if not chat_id:
        print("❌ Error: CHAT_ID not found in environment variables.")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    message = """🤖 German Word Daily Bot - Test Message

✅ Connection successful!
🇩🇪 Ready to send daily German vocabulary lessons.

This is a test message to verify the bot is working correctly."""
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if data['ok']:
            print("✅ Test message sent successfully!")
            print(f"Message ID: {data['result']['message_id']}")
            return True
        else:
            print(f"❌ Telegram API error: {data.get('description', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Telegram Bot Connection")
    print("=" * 40)
    success = test_bot_connection()
    
    if success:
        print("\n🎉 Bot is ready for daily German lessons!")
    else:
        print("\n🔧 Please check your configuration and try again.")
