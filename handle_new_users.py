#!/usr/bin/env python3
"""
New User Registration Handler for German Learning Bot
Processes incoming messages and registers new users
"""

import os
import json
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('user_registration.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class UserRegistrationHandler:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.active_users = self.load_active_users()
        
        logger.info("User registration handler initialized")
    
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
            json.dump(self.active_users, f, indent=2, ensure_ascii=False)
    
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
    
    def register_user(self, chat_id, user_info):
        """Register a new user"""
        chat_id_str = str(chat_id)
        
        if chat_id_str in self.active_users:
            logger.info(f"User {chat_id_str} already registered")
            return False
        
        # Register new user
        self.active_users[chat_id_str] = {
            'first_name': user_info.get('first_name', 'Unknown'),
            'last_name': user_info.get('last_name', ''),
            'username': user_info.get('username', ''),
            'language_code': user_info.get('language_code', 'en'),
            'registered_date': datetime.now().isoformat(),
            'active': True,
            'total_messages': 1
        }
        
        self.save_active_users()
        logger.info(f"New user registered: {user_info.get('first_name', 'Unknown')} ({chat_id_str})")
        return True
    
    def send_welcome_message(self, chat_id, user_info):
        """Send welcome message to new user"""
        first_name = user_info.get('first_name', 'there')
        
        welcome_msg = f"🇩🇪 **Willkommen, {first_name}!** Welcome to German Learning!\n\n"
        welcome_msg += "🎉 You're now registered for our comprehensive German learning system!\n\n"
        
        welcome_msg += "📚 **What you'll receive:**\n"
        welcome_msg += "• 🌅 **Daily lessons** at 9:00 AM UTC with 3 new German words\n"
        welcome_msg += "• 🧠 **Interactive quizzes** on Tue/Thu/Sat at 7:00 PM UTC\n"
        welcome_msg += "• 📊 **Weekly progress reports** every Sunday at 8:00 PM UTC\n"
        welcome_msg += "• 🎯 **CEFR level progression** from A1 (beginner) to B2 (intermediate)\n"
        welcome_msg += "• 🔄 **Spaced repetition** for optimal vocabulary retention\n\n"
        
        welcome_msg += "🎓 **Learning Features:**\n"
        welcome_msg += "• IPA pronunciation guides for authentic German sounds\n"
        welcome_msg += "• Cultural context for appropriate word usage\n"
        welcome_msg += "• Grammar tips integrated with vocabulary\n"
        welcome_msg += "• Personal progress tracking and achievements\n"
        welcome_msg += "• Smart review system based on your learning patterns\n\n"
        
        welcome_msg += "🚀 **Your learning journey starts now!**\n"
        welcome_msg += "You'll receive your first German lesson at the next scheduled time.\n\n"
        
        welcome_msg += "💡 **Tip:** Consistency is key! Try to engage with the daily lessons for best results.\n\n"
        welcome_msg += "**Viel Erfolg beim Deutschlernen!** (Good luck learning German!) 🇩🇪📚"
        
        return self.send_message(chat_id, welcome_msg)
    
    def handle_existing_user_message(self, chat_id, user_info, message_text):
        """Handle message from existing user"""
        chat_id_str = str(chat_id)
        
        # Update message count
        if chat_id_str in self.active_users:
            self.active_users[chat_id_str]['total_messages'] = self.active_users[chat_id_str].get('total_messages', 0) + 1
            self.active_users[chat_id_str]['last_message_date'] = datetime.now().isoformat()
            self.save_active_users()
        
        # Handle common commands/questions
        message_lower = message_text.lower()
        
        if any(word in message_lower for word in ['help', 'hilfe', 'info', 'status']):
            return self.send_status_message(chat_id, user_info)
        elif any(word in message_lower for word in ['stop', 'pause', 'unsubscribe']):
            return self.handle_unsubscribe(chat_id, user_info)
        elif any(word in message_lower for word in ['start', 'resume', 'continue']):
            return self.handle_resubscribe(chat_id, user_info)
        else:
            # General response
            response = f"Hi {user_info.get('first_name', 'there')}! 👋\n\n"
            response += "I'm your German learning companion! 🇩🇪\n\n"
            response += "📚 You'll receive automated lessons, quizzes, and reports.\n"
            response += "💬 Send 'help' for more information or 'stop' to pause lessons.\n\n"
            response += "Keep learning! Your next lesson is coming soon! 🚀"
            
            return self.send_message(chat_id, response)
    
    def send_status_message(self, chat_id, user_info):
        """Send status/help message"""
        first_name = user_info.get('first_name', 'there')
        
        # Get user progress if available
        try:
            from user_progress import UserProgress
            progress = UserProgress(str(chat_id))
            stats = progress.get_stats()
            
            status_msg = f"📊 **{first_name}'s German Learning Status**\n\n"
            status_msg += f"🎯 **Current Level:** {stats['current_level']}\n"
            status_msg += f"📚 **Words Learned:** {stats['total_words_learned']}\n"
            status_msg += f"🔥 **Daily Streak:** {stats['daily_streak']} days\n"
            status_msg += f"📝 **Words Due for Review:** {stats['words_due_for_review']}\n\n"
        except:
            status_msg = f"📊 **{first_name}'s German Learning Status**\n\n"
            status_msg += "🌱 Your learning journey is just beginning!\n\n"
        
        status_msg += "📅 **Schedule:**\n"
        status_msg += "• Daily lessons: 9:00 AM UTC\n"
        status_msg += "• Quizzes: Tue/Thu/Sat 7:00 PM UTC\n"
        status_msg += "• Weekly reports: Sunday 8:00 PM UTC\n\n"
        
        status_msg += "💬 **Commands:**\n"
        status_msg += "• Send 'help' for this status\n"
        status_msg += "• Send 'stop' to pause lessons\n"
        status_msg += "• Send 'start' to resume lessons\n\n"
        
        status_msg += "🇩🇪 Keep up the great work!"
        
        return self.send_message(chat_id, status_msg)
    
    def handle_unsubscribe(self, chat_id, user_info):
        """Handle user unsubscribe request"""
        chat_id_str = str(chat_id)
        first_name = user_info.get('first_name', 'there')
        
        if chat_id_str in self.active_users:
            self.active_users[chat_id_str]['active'] = False
            self.active_users[chat_id_str]['paused_date'] = datetime.now().isoformat()
            self.save_active_users()
        
        response = f"⏸️ **Lessons Paused, {first_name}**\n\n"
        response += "Your German lessons have been paused. You won't receive:\n"
        response += "• Daily vocabulary lessons\n"
        response += "• Quiz sessions\n"
        response += "• Weekly progress reports\n\n"
        response += "📚 Your progress is saved and will be there when you return!\n\n"
        response += "💬 Send 'start' anytime to resume your learning journey.\n\n"
        response += "**Auf Wiedersehen!** (Goodbye!) 👋"
        
        return self.send_message(chat_id, response)
    
    def handle_resubscribe(self, chat_id, user_info):
        """Handle user resubscribe request"""
        chat_id_str = str(chat_id)
        first_name = user_info.get('first_name', 'there')
        
        if chat_id_str in self.active_users:
            self.active_users[chat_id_str]['active'] = True
            self.active_users[chat_id_str]['resumed_date'] = datetime.now().isoformat()
            self.save_active_users()
        
        response = f"🎉 **Welcome Back, {first_name}!**\n\n"
        response += "Your German lessons have been resumed! You'll receive:\n"
        response += "• 🌅 Daily vocabulary lessons\n"
        response += "• 🧠 Interactive quiz sessions\n"
        response += "• 📊 Weekly progress reports\n\n"
        response += "📚 Your previous progress has been preserved!\n\n"
        response += "🚀 Your next lesson will arrive at the scheduled time.\n\n"
        response += "**Willkommen zurück!** (Welcome back!) 🇩🇪"
        
        return self.send_message(chat_id, response)
    
    def process_new_messages(self):
        """Check for new messages and handle them"""
        url = f"{self.api_url}/getUpdates"
        
        try:
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if not data['ok']:
                logger.error(f"Telegram API error: {data.get('description', 'Unknown error')}")
                return False
            
            new_users = 0
            processed_messages = 0
            
            for update in data['result']:
                if 'message' in update:
                    message = update['message']
                    chat_id = message['chat']['id']
                    user_info = message['from']
                    message_text = message.get('text', '')
                    
                    processed_messages += 1
                    
                    # Check if this is a new user
                    if self.register_user(chat_id, user_info):
                        # New user - send welcome message
                        self.send_welcome_message(chat_id, user_info)
                        new_users += 1
                    else:
                        # Existing user - handle their message
                        self.handle_existing_user_message(chat_id, user_info, message_text)
            
            if processed_messages > 0:
                logger.info(f"Processed {processed_messages} messages, {new_users} new users registered")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing new messages: {e}")
            return False
    
    def get_user_statistics(self):
        """Get statistics about registered users"""
        total_users = len(self.active_users)
        active_users = len([u for u in self.active_users.values() if u.get('active', True)])
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users
        }

def main():
    """Main function for user registration handler"""
    try:
        handler = UserRegistrationHandler()
        
        # Process any new messages
        success = handler.process_new_messages()
        
        # Log statistics
        stats = handler.get_user_statistics()
        logger.info(f"User statistics: {stats['active_users']} active, "
                   f"{stats['inactive_users']} inactive, "
                   f"{stats['total_users']} total users")
        
        return success
        
    except Exception as e:
        logger.error(f"Error in user registration handler: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
