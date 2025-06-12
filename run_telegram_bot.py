#!/usr/bin/env python3
"""
Real-Time Telegram Bot Runner
Continuously listens for user messages and processes commands
"""

import os
import time
import json
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import bot handler
try:
    from telegram_bot_handler import TelegramBotHandler
    BOT_HANDLER_AVAILABLE = True
except ImportError as e:
    print(f"❌ Bot handler not available: {e}")
    BOT_HANDLER_AVAILABLE = False
    exit(1)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot_live.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TelegramBotRunner:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN must be set in .env file")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.bot_handler = TelegramBotHandler()
        self.last_update_id = 0
        self.running = False
        
        logger.info("Telegram Bot Runner initialized")
    
    def get_updates(self, offset=None, timeout=30):
        """Get updates from Telegram API"""
        try:
            url = f"{self.api_url}/getUpdates"
            params = {
                'timeout': timeout,
                'allowed_updates': ['message', 'callback_query']
            }
            
            if offset:
                params['offset'] = offset
            
            response = requests.get(url, params=params, timeout=timeout + 5)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    return data['result']
            
            logger.error(f"Failed to get updates: {response.text}")
            return []
            
        except requests.exceptions.Timeout:
            # Timeout is normal for long polling
            return []
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []
    
    def process_updates(self, updates):
        """Process incoming updates"""
        for update in updates:
            try:
                # Update last_update_id
                self.last_update_id = max(self.last_update_id, update['update_id'])
                
                # Process the update
                self.bot_handler.process_update(update)
                
            except Exception as e:
                logger.error(f"Error processing update {update.get('update_id', 'unknown')}: {e}")
    
    def start_polling(self):
        """Start polling for updates"""
        print("STARTING TELEGRAM BOT POLLING")
        print("=" * 50)
        print(f"Bot Token: {self.bot_token[:10]}...")
        print("Polling for updates...")
        print("Bot is now LIVE and ready to respond!")
        print("Try sending /start to your bot now!")
        print("=" * 50)
        print("Bot Commands Available:")
        print("   /start - Begin German learning journey")
        print("   /lesson - Get daily German words")
        print("   /quiz - Take adaptive quiz")
        print("   /stats - View progress")
        print("   /analytics - Detailed insights")
        print("   /streak - Check streak")
        print("   /help - Show all commands")
        print("   /stop - Pause lessons")
        print("=" * 50)
        print("Press Ctrl+C to stop the bot")
        print("=" * 50)
        
        self.running = True
        
        try:
            while self.running:
                # Get updates with long polling
                updates = self.get_updates(offset=self.last_update_id + 1, timeout=30)
                
                if updates:
                    logger.info(f"Received {len(updates)} updates")
                    self.process_updates(updates)
                
                # Small delay to prevent excessive API calls
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nBot stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Fatal error in polling: {e}")
            self.running = False
    
    def stop_polling(self):
        """Stop polling"""
        self.running = False
        logger.info("Bot polling stopped")
    
    def test_bot_connection(self):
        """Test bot connection"""
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    bot_info = data['result']
                    print("Bot connected successfully!")
                    print(f"   Bot Name: {bot_info.get('first_name')}")
                    print(f"   Username: @{bot_info.get('username')}")
                    print(f"   Bot ID: {bot_info.get('id')}")
                    return True

            print(f"Bot connection failed: {response.text}")
            return False

        except Exception as e:
            print(f"Error testing bot connection: {e}")
            return False
    
    def send_startup_message(self):
        """Send startup message to admin"""
        try:
            admin_chat_id = os.getenv('CHAT_ID')
            if not admin_chat_id:
                return
            
            startup_message = """
**German Daily Word Bot is NOW LIVE!**

Bot is actively listening for commands
Real-time message processing enabled
All commands are now functional

**Test Commands:**
/start - Begin learning journey
/lesson - Get daily German words
/quiz - Take adaptive quiz
/stats - View your progress
/help - See all commands

**Your bot is ready for users!**
Share: https://t.me/Germandailywordbot
"""
            
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': admin_chat_id,
                'text': startup_message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("Startup message sent to admin")
            else:
                logger.warning(f"Failed to send startup message: {response.text}")
                
        except Exception as e:
            logger.warning(f"Error sending startup message: {e}")

def main():
    """Main function to run the bot"""
    try:
        if not BOT_HANDLER_AVAILABLE:
            print("Bot handler not available")
            return False
        
        # Initialize bot runner
        bot_runner = TelegramBotRunner()
        
        # Test connection
        if not bot_runner.test_bot_connection():
            print("Cannot connect to bot. Check your BOT_TOKEN.")
            return False
        
        # Send startup notification
        bot_runner.send_startup_message()
        
        # Start polling
        bot_runner.start_polling()
        
        return True
        
    except Exception as e:
        logger.error(f"Fatal error running bot: {e}")
        print(f"Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
