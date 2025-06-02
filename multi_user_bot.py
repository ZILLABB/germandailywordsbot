#!/usr/bin/env python3
"""
Multi-User German Learning Bot
Serves multiple users with individual progress tracking
"""

import os
import json
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import enhanced modules
try:
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    ENHANCED_MODE = True
except ImportError:
    ENHANCED_MODE = False

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiUserGermanBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.vocabulary_manager = VocabularyManager() if ENHANCED_MODE else None
        
        # Store for active users
        self.active_users = self.load_active_users()
        
        logger.info("Multi-user German bot initialized")
    
    def load_active_users(self):
        """Load list of active users"""
        try:
            with open('active_users.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_active_users(self):
        """Save active users list"""
        with open('active_users.json', 'w') as f:
            json.dump(self.active_users, f, indent=2)
    
    def register_user(self, chat_id, user_info):
        """Register a new user"""
        chat_id_str = str(chat_id)
        if chat_id_str not in self.active_users:
            self.active_users[chat_id_str] = {
                'first_name': user_info.get('first_name', 'Unknown'),
                'username': user_info.get('username', ''),
                'registered_date': datetime.now().isoformat(),
                'active': True
            }
            self.save_active_users()
            logger.info(f"New user registered: {chat_id_str}")
            return True
        return False
    
    def send_message(self, chat_id, message):
        """Send message to specific user"""
        url = f"{self.api_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()['ok']
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {e}")
            return False
    
    def send_daily_lesson_to_user(self, chat_id):
        """Send personalized daily lesson to a specific user"""
        try:
            if not ENHANCED_MODE:
                # Basic lesson
                message = "🇩🇪 **Daily German Word**\n\nHallo - Hello\n🔊 /ˈhaloː/\n📝 Hallo, wie geht es dir?\n💭 Hello, how are you?"
                return self.send_message(chat_id, message)
            
            # Enhanced lesson with progress tracking
            user_progress = UserProgress(str(chat_id), self.vocabulary_manager)

            # Get user's current level and learned words
            user_level = user_progress.get_current_level()
            learned_words = []
            for level_data in user_progress.data['words_by_level'].values():
                learned_words.extend(level_data['learned'])

            # Get progressive words
            daily_words = self.vocabulary_manager.get_progressive_words(
                user_level, 3, learned_words
            )

            if not daily_words:
                return False

            # Format enhanced message
            message = self.format_user_lesson(daily_words, user_progress)

            # Send lesson
            success = self.send_message(chat_id, message)

            if success:
                # Update progress with enhanced tracking
                streak_info = user_progress.update_daily_streak(daily_words)
                for word in daily_words:
                    if 'level' not in word:
                        word['level'] = 'A1'
                    user_progress.add_learned_word(word)

                # Add streak message if milestone reached
                if streak_info and (streak_info.get('milestone_reached') or
                                  streak_info.get('grace_period_used') or
                                  streak_info.get('streak_recovered')):
                    streak_message = user_progress.get_streak_message(streak_info)
                    self.send_message(chat_id, f"\n\n{streak_message}")

                user_progress.save_progress()
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending lesson to {chat_id}: {e}")
            return False
    
    def format_user_lesson(self, words, user_progress):
        """Format lesson for individual user"""
        stats = user_progress.get_stats()
        today = datetime.now().strftime('%A, %B %d, %Y')
        
        message = f"🌅 **Your German Learning Journey**\n"
        message += f"📅 {today}\n"
        message += f"🎯 Level: {stats['current_level']} | "
        message += f"📚 Words: {stats['total_words_learned']} | "
        message += f"🔥 Streak: {stats['daily_streak']} days\n\n"
        
        for i, word in enumerate(words, 1):
            level_emoji = {"A1": "🟢", "A2": "🟡", "B1": "🟠", "B2": "🔴"}
            emoji = level_emoji.get(word.get('level', 'A1'), '⚪')
            
            message += f"**{i}. {word['german']}** {emoji}\n"
            message += f"🇺🇸 {word['english']}\n"
            message += f"🔊 {word['pronunciation']}\n"
            message += f"📝 {word['example']}\n"
            message += f"💭 _{word['example_translation']}_\n\n"
        
        message += "🎯 Keep up the great work! 🇩🇪"
        return message
    
    def send_daily_lessons_to_all(self):
        """Send daily lessons to all active users"""
        success_count = 0
        total_users = len([u for u in self.active_users.values() if u['active']])
        
        logger.info(f"Sending daily lessons to {total_users} active users")
        
        for chat_id, user_info in self.active_users.items():
            if user_info['active']:
                if self.send_daily_lesson_to_user(chat_id):
                    success_count += 1
                    logger.info(f"Lesson sent to {user_info['first_name']} ({chat_id})")
                else:
                    logger.error(f"Failed to send lesson to {chat_id}")
        
        logger.info(f"Daily lessons completed: {success_count}/{total_users} successful")
        return success_count, total_users
    
    def handle_new_messages(self):
        """Check for new messages and register users"""
        url = f"{self.api_url}/getUpdates"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if data['ok']:
                for update in data['result']:
                    if 'message' in update:
                        message = update['message']
                        chat_id = message['chat']['id']
                        user_info = message['from']
                        
                        # Register new user
                        if self.register_user(chat_id, user_info):
                            welcome_msg = f"🇩🇪 **Welcome to German Learning!**\n\n"
                            welcome_msg += f"Hello {user_info.get('first_name', 'there')}! 👋\n\n"
                            welcome_msg += "You're now registered for daily German lessons!\n"
                            welcome_msg += "📚 Daily lessons at 9:00 AM UTC\n"
                            welcome_msg += "🧠 Quizzes 3x per week\n"
                            welcome_msg += "📊 Weekly progress reports\n\n"
                            welcome_msg += "Your learning journey begins now! 🚀"
                            
                            self.send_message(chat_id, welcome_msg)
            
        except Exception as e:
            logger.error(f"Error handling new messages: {e}")
    
    def get_user_stats(self):
        """Get statistics about all users"""
        total_users = len(self.active_users)
        active_users = len([u for u in self.active_users.values() if u['active']])
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'registration_dates': [u['registered_date'] for u in self.active_users.values()]
        }

def main():
    """Main function for multi-user bot"""
    try:
        bot = MultiUserGermanBot()
        
        # Check for new users first
        bot.handle_new_messages()
        
        # Send daily lessons to all active users
        success, total = bot.send_daily_lessons_to_all()
        
        # Log statistics
        stats = bot.get_user_stats()
        logger.info(f"Bot statistics: {stats['active_users']} active users, "
                   f"{success}/{total} lessons delivered successfully")
        
        return success == total
        
    except Exception as e:
        logger.error(f"Error in multi-user bot: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
