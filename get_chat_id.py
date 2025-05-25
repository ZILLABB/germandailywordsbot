#!/usr/bin/env python3
"""
Script to retrieve your Telegram chat ID.
Run this after creating your bot and sending it a test message.
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_chat_id():
    """
    Retrieve chat ID by calling Telegram's getUpdates API.
    Make sure to send a message to your bot first!
    """
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        print("❌ Error: BOT_TOKEN not found in environment variables.")
        print("Please create a .env file with your bot token:")
        print("BOT_TOKEN=your_bot_token_here")
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        if not data['ok']:
            print(f"❌ Telegram API error: {data.get('description', 'Unknown error')}")
            return
        
        updates = data['result']
        
        if not updates:
            print("❌ No messages found!")
            print("Please send a message to your bot first, then run this script again.")
            return
        
        # Get the most recent message
        latest_update = updates[-1]
        chat_id = latest_update['message']['chat']['id']
        chat_type = latest_update['message']['chat']['type']
        
        print("✅ Success! Here's your chat information:")
        print(f"Chat ID: {chat_id}")
        print(f"Chat Type: {chat_type}")
        
        if chat_type == 'private':
            first_name = latest_update['message']['chat'].get('first_name', 'Unknown')
            print(f"User: {first_name}")
        
        print("\n📝 Add this to your .env file:")
        print(f"CHAT_ID={chat_id}")
        
        return chat_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except KeyError as e:
        print(f"❌ Unexpected response format: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🤖 Telegram Chat ID Retriever")
    print("=" * 40)
    get_chat_id()
