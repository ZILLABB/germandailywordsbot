#!/usr/bin/env python3
"""
German Daily Word Bot - Main Application
Sends 3-5 German vocabulary words daily via Telegram
"""

import json
import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GermanWordBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.chat_id = os.getenv('CHAT_ID')
        self.words_per_day = int(os.getenv('WORDS_PER_DAY', '3'))  # Default to 3 words
        
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        if not self.chat_id:
            raise ValueError("CHAT_ID environment variable is required")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.words = self.load_words()
        
        logger.info(f"Bot initialized with {len(self.words)} words, sending {self.words_per_day} words per day")
    
    def load_words(self):
        """Load German vocabulary from JSON file"""
        try:
            with open('words.json', 'r', encoding='utf-8') as f:
                words = json.load(f)
            logger.info(f"Loaded {len(words)} words from vocabulary database")
            return words
        except FileNotFoundError:
            logger.error("words.json file not found")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing words.json: {e}")
            raise
    
    def get_daily_words(self):
        """
        Get words for today using deterministic selection based on date.
        This ensures the same words are sent if the script runs multiple times on the same day.
        """
        today = datetime.now()
        # Create a seed based on the current date
        date_seed = today.year * 10000 + today.month * 100 + today.day
        
        # Use the date as a seed to get consistent daily selection
        import random
        random.seed(date_seed)
        
        # Select words for today
        selected_words = random.sample(self.words, min(self.words_per_day, len(self.words)))
        
        logger.info(f"Selected {len(selected_words)} words for {today.strftime('%Y-%m-%d')}")
        return selected_words
    
    def format_word_message(self, word_data):
        """Format a single word into a beautiful message"""
        message = f"🇩🇪 **{word_data['german']}**\n"
        message += f"🇺🇸 {word_data['english']}\n"
        message += f"🔊 {word_data['pronunciation']}\n\n"
        message += f"📝 *Example:*\n"
        message += f"• {word_data['example']}\n"
        message += f"• {word_data['example_translation']}\n\n"
        message += f"📂 Category: {word_data['category'].replace('_', ' ').title()}"
        
        return message
    
    def format_daily_message(self, words):
        """Format the complete daily message with multiple words"""
        today = datetime.now().strftime('%A, %B %d, %Y')
        
        header = f"🌅 **German Words of the Day**\n"
        header += f"📅 {today}\n"
        header += f"📚 Today's vocabulary lesson ({len(words)} words)\n"
        header += "=" * 40 + "\n\n"
        
        word_messages = []
        for i, word in enumerate(words, 1):
            word_msg = f"**{i}. {word['german']}**\n"
            word_msg += f"🇺🇸 {word['english']}\n"
            word_msg += f"🔊 {word['pronunciation']}\n"
            word_msg += f"📝 {word['example']}\n"
            word_msg += f"💭 _{word['example_translation']}_\n"
            word_messages.append(word_msg)
        
        footer = "\n" + "=" * 40 + "\n"
        footer += "🎯 **Practice Tip:** Try using these words in your own sentences today!\n"
        footer += "🔄 New words tomorrow at the same time.\n"
        footer += "📖 Keep learning, keep growing! 🌱"
        
        complete_message = header + "\n\n".join(word_messages) + footer
        
        return complete_message
    
    def send_message(self, message):
        """Send message via Telegram Bot API"""
        url = f"{self.api_url}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data['ok']:
                logger.info(f"Message sent successfully. Message ID: {data['result']['message_id']}")
                return True
            else:
                logger.error(f"Telegram API error: {data.get('description', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False
    
    def run(self):
        """Main execution method"""
        try:
            logger.info("Starting German Word Bot daily lesson")
            
            # Get today's words
            daily_words = self.get_daily_words()
            
            # Format the message
            message = self.format_daily_message(daily_words)
            
            # Send the message
            success = self.send_message(message)
            
            if success:
                logger.info("Daily German lesson sent successfully!")
                word_list = [word['german'] for word in daily_words]
                logger.info(f"Words sent: {', '.join(word_list)}")
            else:
                logger.error("Failed to send daily lesson")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error in bot execution: {e}")
            return False

def main():
    """Entry point for the application"""
    try:
        bot = GermanWordBot()
        success = bot.run()
        exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
