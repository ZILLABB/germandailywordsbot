#!/usr/bin/env python3
"""
Multi-User Setup and Management System
Configures the bot for multiple users and manages user registration
"""

import os
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class MultiUserManager:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN must be set in .env file")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.active_users_file = "active_users.json"
        self.webhook_url = None  # Set this for webhook deployment
        
        # Load or create active users database
        self.active_users = self.load_active_users()
        
        logger.info("Multi-User Manager initialized")
    
    def load_active_users(self):
        """Load active users database"""
        try:
            if os.path.exists(self.active_users_file):
                with open(self.active_users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logger.error(f"Error loading active users: {e}")
            return {}
    
    def save_active_users(self):
        """Save active users database"""
        try:
            with open(self.active_users_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_users, f, indent=2, ensure_ascii=False)
            logger.info(f"Active users saved: {len(self.active_users)} users")
        except Exception as e:
            logger.error(f"Error saving active users: {e}")
    
    def register_user(self, chat_id, user_info=None):
        """Register a new user"""
        chat_id_str = str(chat_id)
        
        if chat_id_str not in self.active_users:
            user_data = {
                'chat_id': chat_id_str,
                'registration_date': datetime.now().isoformat(),
                'status': 'active',
                'preferences': {
                    'words_per_day': 3,
                    'quiz_frequency': 'auto',
                    'analytics_reports': True
                }
            }
            
            # Add user info if provided
            if user_info:
                user_data.update(user_info)
            
            self.active_users[chat_id_str] = user_data
            self.save_active_users()
            
            logger.info(f"New user registered: {chat_id}")
            return True
        else:
            logger.info(f"User already registered: {chat_id}")
            return False
    
    def get_user_info(self, chat_id):
        """Get user information"""
        return self.active_users.get(str(chat_id))
    
    def update_user_preferences(self, chat_id, preferences):
        """Update user preferences"""
        chat_id_str = str(chat_id)
        if chat_id_str in self.active_users:
            self.active_users[chat_id_str]['preferences'].update(preferences)
            self.save_active_users()
            return True
        return False
    
    def deactivate_user(self, chat_id):
        """Deactivate a user"""
        chat_id_str = str(chat_id)
        if chat_id_str in self.active_users:
            self.active_users[chat_id_str]['status'] = 'inactive'
            self.save_active_users()
            return True
        return False
    
    def get_active_users_list(self):
        """Get list of active users"""
        return [
            chat_id for chat_id, data in self.active_users.items()
            if data.get('status') == 'active'
        ]
    
    def send_welcome_message(self, chat_id):
        """Send welcome message to new user"""
        welcome_text = """
🎉 **Welcome to German Daily Word Bot!** 🇩🇪

I'm your personal German learning assistant with advanced features:

🌟 **What I offer:**
📚 Daily German lessons (3-5 words with pronunciation)
🔥 Advanced streak tracking with milestones & rewards
🧠 Adaptive quizzes with 6 different question types
📊 Comprehensive learning analytics & insights
📈 Weekly progress reports & personalized recommendations

🚀 **Getting Started:**
• You'll receive daily lessons automatically
• Take quizzes when prompted to test your knowledge
• Track your progress with detailed analytics
• Build learning streaks and earn achievements!

🎯 **Your Learning Journey:**
• Start with A1 level vocabulary
• Progress through A2, B1, B2 as you improve
• Get personalized difficulty adjustment
• Master German with intelligent spaced repetition

Type /help for commands or just wait for your first lesson!

**Viel Erfolg beim Deutschlernen!** 🚀
(Good luck learning German!)
"""
        
        return self.send_message(chat_id, welcome_text)
    
    def send_message(self, chat_id, text):
        """Send message to user"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Failed to send message to {chat_id}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {e}")
            return False
    
    def setup_webhook(self, webhook_url):
        """Setup webhook for real-time bot responses"""
        try:
            url = f"{self.api_url}/setWebhook"
            data = {'url': webhook_url}
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logger.info(f"Webhook set successfully: {webhook_url}")
                return True
            else:
                logger.error(f"Failed to set webhook: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    def remove_webhook(self):
        """Remove webhook (for polling mode)"""
        try:
            url = f"{self.api_url}/deleteWebhook"
            response = requests.post(url)
            
            if response.status_code == 200:
                logger.info("Webhook removed successfully")
                return True
            else:
                logger.error(f"Failed to remove webhook: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing webhook: {e}")
            return False
    
    def get_bot_info(self):
        """Get bot information"""
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    bot_info = data['result']
                    return {
                        'username': bot_info.get('username'),
                        'first_name': bot_info.get('first_name'),
                        'id': bot_info.get('id')
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None
    
    def create_user_onboarding_flow(self, chat_id):
        """Create personalized onboarding for new users"""
        try:
            # Send welcome message
            if not self.send_welcome_message(chat_id):
                return False
            
            # Register user
            self.register_user(chat_id)
            
            # Initialize user progress
            from user_progress import UserProgress
            from vocabulary_manager import VocabularyManager
            
            vocab_manager = VocabularyManager()
            user_progress = UserProgress(str(chat_id), vocab_manager)
            
            # Send first lesson immediately
            from multi_user_bot import MultiUserGermanBot
            bot = MultiUserGermanBot()
            bot.send_daily_lesson_to_user(chat_id)
            
            logger.info(f"User onboarding completed for {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error in user onboarding: {e}")
            return False
    
    def generate_user_statistics(self):
        """Generate statistics about bot usage"""
        total_users = len(self.active_users)
        active_users = len(self.get_active_users_list())
        
        # Calculate registration trends
        recent_registrations = 0
        for user_data in self.active_users.values():
            reg_date = datetime.fromisoformat(user_data['registration_date'])
            days_ago = (datetime.now() - reg_date).days
            if days_ago <= 7:
                recent_registrations += 1
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'recent_registrations': recent_registrations,
            'registration_rate': f"{(recent_registrations/7):.1f} users/day" if recent_registrations > 0 else "0 users/day"
        }

def setup_multi_user_bot():
    """Setup bot for multi-user access"""
    print("🤖 SETTING UP MULTI-USER GERMAN DAILY WORD BOT")
    print("=" * 50)
    
    try:
        manager = MultiUserManager()
        
        # Get bot info
        bot_info = manager.get_bot_info()
        if bot_info:
            print(f"✅ Bot connected: @{bot_info['username']}")
            print(f"   Bot Name: {bot_info['first_name']}")
            print(f"   Bot ID: {bot_info['id']}")
        else:
            print("❌ Failed to connect to bot")
            return False
        
        # Remove any existing webhook (for polling mode)
        manager.remove_webhook()
        
        # Setup initial user (you)
        your_chat_id = os.getenv('CHAT_ID')
        if your_chat_id:
            manager.register_user(your_chat_id, {
                'username': 'Bot Owner',
                'role': 'admin'
            })
            print(f"✅ Admin user registered: {your_chat_id}")
        
        # Generate bot link
        bot_username = bot_info['username'] if bot_info else 'your_bot'
        bot_link = f"https://t.me/{bot_username}"
        
        print(f"\n🔗 **Bot Link:** {bot_link}")
        print(f"📱 **Share this link** for others to start the bot!")
        
        # Display setup instructions
        print(f"\n📋 **MULTI-USER SETUP COMPLETE!**")
        print(f"   • Bot is ready for multiple users")
        print(f"   • Users can start the bot at: {bot_link}")
        print(f"   • Active users database: {manager.active_users_file}")
        print(f"   • Current users: {len(manager.active_users)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up multi-user bot: {e}")
        return False

def main():
    """Main setup function"""
    return setup_multi_user_bot()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
