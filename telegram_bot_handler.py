#!/usr/bin/env python3
"""
Telegram Bot Handler for Real-time User Interactions
Handles /start, /help, /quiz, /stats commands and user registration
"""

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import bot modules
try:
    from multi_user_setup import MultiUserManager
    from multi_user_bot import MultiUserGermanBot
    from send_quiz import GermanQuizBot
    from analytics_dashboard import AnalyticsDashboard
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    BOT_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Bot modules not available: {e}")
    BOT_MODULES_AVAILABLE = False

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TelegramBotHandler:
    def __init__(self):
        if not BOT_MODULES_AVAILABLE:
            raise ImportError("Required bot modules not available")
        
        self.user_manager = MultiUserManager()
        self.vocabulary_manager = VocabularyManager()
        
        # Bot commands
        self.commands = {
            '/start': self.handle_start,
            '/help': self.handle_help,
            '/lesson': self.handle_lesson,
            '/quiz': self.handle_quiz,
            '/stats': self.handle_stats,
            '/analytics': self.handle_analytics,
            '/preferences': self.handle_preferences,
            '/streak': self.handle_streak,
            '/stop': self.handle_stop
        }
        
        logger.info("Telegram Bot Handler initialized")
    
    def process_update(self, update_data):
        """Process incoming Telegram update"""
        try:
            if 'message' not in update_data:
                return
            
            message = update_data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            
            # Log incoming message
            user_name = message.get('from', {}).get('first_name', 'Unknown')
            logger.info(f"Message from {user_name} ({chat_id}): {text}")
            
            # Handle commands
            if text.startswith('/'):
                command = text.split()[0].lower()
                if command in self.commands:
                    self.commands[command](chat_id, message)
                else:
                    self.handle_unknown_command(chat_id, text)
            else:
                # Handle regular text (could be quiz answers, etc.)
                self.handle_text_message(chat_id, text, message)
                
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    def handle_start(self, chat_id, message):
        """Handle /start command - user registration and onboarding"""
        try:
            user_info = {
                'username': message.get('from', {}).get('username', ''),
                'first_name': message.get('from', {}).get('first_name', ''),
                'last_name': message.get('from', {}).get('last_name', ''),
                'language_code': message.get('from', {}).get('language_code', 'en')
            }
            
            # Check if user is already registered
            existing_user = self.user_manager.get_user_info(chat_id)
            
            if existing_user:
                # Welcome back message
                welcome_back = f"""
🎉 **Welcome back, {user_info['first_name']}!** 🇩🇪

Your German learning journey continues! Here's what's available:

📚 /lesson - Get today's German words
🧠 /quiz - Take an adaptive quiz
📊 /stats - View your progress
📈 /analytics - Detailed learning insights
🔥 /streak - Check your learning streak
⚙️ /preferences - Customize your experience
❓ /help - See all commands

Ready to continue learning? 🚀
"""
                self.user_manager.send_message(chat_id, welcome_back)
            else:
                # New user onboarding
                success = self.user_manager.create_user_onboarding_flow(chat_id)
                if success:
                    logger.info(f"New user onboarded: {chat_id}")
                else:
                    logger.error(f"Failed to onboard user: {chat_id}")
            
        except Exception as e:
            logger.error(f"Error handling /start: {e}")
            self.user_manager.send_message(chat_id, "❌ Sorry, there was an error. Please try again.")
    
    def handle_help(self, chat_id, message):
        """Handle /help command"""
        help_text = """
🤖 **German Daily Word Bot - Commands** 🇩🇪

📚 **Learning Commands:**
/lesson - Get today's German lesson
/quiz - Take an adaptive quiz
/stats - View your learning progress
/analytics - Detailed analytics report
/streak - Check your learning streak

⚙️ **Settings:**
/preferences - Customize your learning experience

🆘 **Support:**
/help - Show this help message
/stop - Pause daily lessons

🌟 **Features:**
• Daily German lessons with pronunciation
• Adaptive quizzes with 6 question types
• Advanced streak tracking with milestones
• Comprehensive learning analytics
• Personalized difficulty adjustment
• Weekly progress reports

**Happy learning!** 🚀
"""
        self.user_manager.send_message(chat_id, help_text)
    
    def handle_lesson(self, chat_id, message):
        """Handle /lesson command - send daily lesson"""
        try:
            bot = MultiUserGermanBot()
            success = bot.send_daily_lesson_to_user(chat_id)
            
            if not success:
                self.user_manager.send_message(
                    chat_id, 
                    "📚 You've already received today's lesson! Come back tomorrow for more German words. 🇩🇪"
                )
                
        except Exception as e:
            logger.error(f"Error handling /lesson: {e}")
            self.user_manager.send_message(chat_id, "❌ Sorry, couldn't send lesson. Please try again.")
    
    def handle_quiz(self, chat_id, message):
        """Handle /quiz command - send adaptive quiz"""
        try:
            # Initialize user progress to ensure they have learned words
            user_progress = UserProgress(str(chat_id), self.vocabulary_manager)
            
            # Check if user has enough words for quiz
            total_words = user_progress.get_stats()['total_words_learned']
            
            if total_words < 5:
                self.user_manager.send_message(
                    chat_id,
                    "📚 You need to learn at least 5 words before taking a quiz!\n"
                    "Use /lesson to get your daily German words first. 🇩🇪"
                )
                return
            
            # Send adaptive quiz
            quiz_bot = GermanQuizBot()
            quiz_bot.chat_id = str(chat_id)  # Override chat ID
            quiz_bot.user_progress = user_progress
            
            success = quiz_bot.send_vocabulary_quiz('adaptive')
            
            if not success:
                self.user_manager.send_message(
                    chat_id,
                    "🧠 No quiz available right now. Try again later or learn more words first!"
                )
                
        except Exception as e:
            logger.error(f"Error handling /quiz: {e}")
            self.user_manager.send_message(chat_id, "❌ Sorry, couldn't send quiz. Please try again.")
    
    def handle_stats(self, chat_id, message):
        """Handle /stats command - show user statistics"""
        try:
            user_progress = UserProgress(str(chat_id), self.vocabulary_manager)
            stats = user_progress.get_stats()
            
            stats_message = f"""
📊 **Your German Learning Stats** 📊

🎓 **Level:** {stats['current_level']}
📚 **Words Learned:** {stats['total_words_learned']}
🔥 **Current Streak:** {stats['daily_streak']} days
🏆 **Achievements:** {stats['achievements_count']}
📝 **Words for Review:** {stats['words_due_for_review']}

📈 **Progress by Level:**
"""
            
            for level, count in stats['words_by_level'].items():
                if count > 0:
                    stats_message += f"   {level}: {count} words\n"
            
            stats_message += "\n🚀 Keep up the great work!"
            
            self.user_manager.send_message(chat_id, stats_message)
            
        except Exception as e:
            logger.error(f"Error handling /stats: {e}")
            self.user_manager.send_message(chat_id, "❌ Sorry, couldn't get stats. Please try again.")
    
    def handle_analytics(self, chat_id, message):
        """Handle /analytics command - send detailed analytics"""
        try:
            dashboard = AnalyticsDashboard()
            success = dashboard.send_analytics_report(str(chat_id), 'comprehensive')
            
            if not success:
                self.user_manager.send_message(
                    chat_id,
                    "📊 Analytics report couldn't be generated. Make sure you have some learning activity first!"
                )
                
        except Exception as e:
            logger.error(f"Error handling /analytics: {e}")
            self.user_manager.send_message(chat_id, "❌ Sorry, couldn't send analytics. Please try again.")
    
    def handle_streak(self, chat_id, message):
        """Handle /streak command - show streak information"""
        try:
            user_progress = UserProgress(str(chat_id), self.vocabulary_manager)
            
            if hasattr(user_progress, 'streak_manager') and user_progress.streak_manager:
                streak_stats = user_progress.streak_manager.get_streak_stats()
                
                streak_message = f"""
🔥 **Your Learning Streak** 🔥

📊 **Current Streak:** {streak_stats['current_streak']} days
🏆 **Longest Streak:** {streak_stats['longest_streak']} days
📚 **Total Study Days:** {streak_stats['total_study_days']}
🎖️ **Milestones Achieved:** {streak_stats['streak_milestones_achieved']}

🛡️ **Streak Protection:**
❄️ Freezes Available: {streak_stats['streak_freeze_available']}
📈 Consistency Rate: {streak_stats['streak_percentage']:.1f}%
"""
                
                if streak_stats['next_milestone']:
                    streak_message += f"\n🎯 **Next Goal:** {streak_stats['next_milestone']} days"
                    streak_message += f" ({streak_stats['days_to_next_milestone']} to go!)"
                
                streak_message += "\n\n💪 Keep learning daily to build your streak!"
                
            else:
                streak_message = f"""
🔥 **Your Learning Streak** 🔥

📊 **Current Streak:** {user_progress.data.get('daily_streak', 0)} days

💪 Keep learning daily to build your streak!
Use /lesson to get today's German words.
"""
            
            self.user_manager.send_message(chat_id, streak_message)
            
        except Exception as e:
            logger.error(f"Error handling /streak: {e}")
            self.user_manager.send_message(chat_id, "❌ Sorry, couldn't get streak info. Please try again.")
    
    def handle_preferences(self, chat_id, message):
        """Handle /preferences command"""
        preferences_text = """
⚙️ **Learning Preferences** ⚙️

Current settings can be customized:
• Words per day: 3-5 words
• Quiz frequency: Automatic based on progress
• Analytics reports: Weekly summaries
• Difficulty progression: Adaptive

To modify preferences, contact the bot administrator.
More customization options coming soon! 🚀
"""
        self.user_manager.send_message(chat_id, preferences_text)
    
    def handle_stop(self, chat_id, message):
        """Handle /stop command - pause lessons"""
        try:
            success = self.user_manager.deactivate_user(chat_id)
            
            if success:
                stop_message = """
⏸️ **Daily lessons paused** ⏸️

You won't receive automatic daily lessons anymore.
Your progress is saved and you can resume anytime!

To resume: Send /start
To get a lesson: Send /lesson
To take a quiz: Send /quiz

**Auf Wiedersehen!** 👋
"""
            else:
                stop_message = "❌ Couldn't pause lessons. Please try again."
            
            self.user_manager.send_message(chat_id, stop_message)
            
        except Exception as e:
            logger.error(f"Error handling /stop: {e}")
            self.user_manager.send_message(chat_id, "❌ Sorry, there was an error. Please try again.")
    
    def handle_unknown_command(self, chat_id, text):
        """Handle unknown commands"""
        unknown_message = f"""
❓ **Unknown command:** {text}

Try these commands instead:
📚 /lesson - Get today's German lesson
🧠 /quiz - Take a quiz
📊 /stats - View your progress
❓ /help - See all commands

**Tip:** Use /help to see all available commands! 🤖
"""
        self.user_manager.send_message(chat_id, unknown_message)
    
    def handle_text_message(self, chat_id, text, message):
        """Handle regular text messages"""
        # For now, just provide helpful guidance
        help_message = """
💬 **Thanks for your message!**

I understand commands that start with /
Try these:
📚 /lesson - Get German words
🧠 /quiz - Take a quiz
📊 /stats - See your progress
❓ /help - All commands

**Ready to learn German?** 🇩🇪
"""
        self.user_manager.send_message(chat_id, help_message)

# For webhook deployment (Flask/FastAPI integration)
def create_webhook_handler():
    """Create webhook handler for deployment"""
    handler = TelegramBotHandler()
    
    def process_telegram_update(update_json):
        """Process incoming webhook update"""
        try:
            handler.process_update(update_json)
            return {"status": "ok"}
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return {"status": "error", "message": str(e)}
    
    return process_telegram_update

def main():
    """Main function for testing bot handler"""
    try:
        handler = TelegramBotHandler()
        print("Telegram Bot Handler initialized successfully")
        print("Ready to process user commands")
        return True

    except Exception as e:
        print(f"Error initializing bot handler: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
