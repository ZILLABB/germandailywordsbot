#!/usr/bin/env python3
"""
Multi-User Weekly Reports for German Learning Bot
Sends personalized weekly reports to all registered users
"""

import os
import json
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import enhanced modules
try:
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    from progress_stats import ProgressAnalytics
    ENHANCED_MODE = True
except ImportError:
    ENHANCED_MODE = False
    print("Enhanced modules not available. Weekly reports require enhanced mode.")
    exit(1)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_user_reports.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MultiUserReportsBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.vocabulary_manager = VocabularyManager()
        
        # Load active users
        self.active_users = self.load_active_users()
        
        logger.info(f"Multi-user reports bot initialized for {len(self.active_users)} users")
    
    def load_active_users(self):
        """Load list of active users"""
        try:
            with open('active_users.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("No active_users.json found - no users to send reports to")
            return {}
    
    def send_message(self, chat_id, message):
        """Send message to specific user with automatic splitting"""
        url = f"{self.api_url}/sendMessage"
        
        # Split long messages
        max_length = 4000
        if len(message) <= max_length:
            messages = [message]
        else:
            # Split at logical points
            parts = message.split('\n\n')
            messages = []
            current_message = ""
            
            for part in parts:
                if len(current_message + part + '\n\n') <= max_length:
                    current_message += part + '\n\n'
                else:
                    if current_message:
                        messages.append(current_message.strip())
                    current_message = part + '\n\n'
            
            if current_message:
                messages.append(current_message.strip())
        
        # Send all message parts
        success_count = 0
        for i, msg in enumerate(messages):
            payload = {
                'chat_id': chat_id,
                'text': msg,
                'parse_mode': 'Markdown'
            }
            
            try:
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if data['ok']:
                    success_count += 1
                    if len(messages) > 1:
                        logger.info(f"Report part {i+1}/{len(messages)} sent to {chat_id}")
                else:
                    logger.error(f"Telegram API error for {chat_id}: {data.get('description', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Error sending message part {i+1} to {chat_id}: {e}")
        
        return success_count == len(messages)
    
    def generate_user_report(self, chat_id):
        """Generate personalized weekly report for a user"""
        try:
            user_progress = UserProgress(str(chat_id))
            analytics = ProgressAnalytics(str(chat_id))
            
            # Get user info
            user_info = self.active_users.get(str(chat_id), {})
            user_name = user_info.get('first_name', 'there')
            
            # Check if user has enough activity
            stats = user_progress.get_stats()
            if stats['total_words_learned'] < 3:
                # Send encouragement instead
                encouragement = f"🌱 **Keep Going, {user_name}!**\n\n"
                encouragement += "You're building momentum in your German learning journey! "
                encouragement += "Complete a few more daily lessons to unlock your first comprehensive weekly report.\n\n"
                encouragement += f"🎯 **Current Progress:** {stats['total_words_learned']} words learned\n"
                encouragement += "📚 **Goal:** Learn 5+ words to get detailed analytics\n\n"
                encouragement += "🔥 Keep up the daily practice - consistency is key! 🇩🇪"
                
                return encouragement
            
            # Generate comprehensive report
            weekly_report = analytics.generate_weekly_report()
            insights = analytics.generate_learning_insights()
            
            # Add personalized header
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday() + 1)
            week_end = week_start + timedelta(days=6)
            
            header = f"📊 **{user_name}'s Weekly German Report**\n"
            header += f"📅 Week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}\n"
            header += "🇩🇪 Your personalized learning analytics\n\n"
            
            # Add motivational section
            motivation = self.generate_motivation(stats, user_name)
            
            # Combine all sections
            full_report = header + weekly_report + "\n\n" + insights + "\n\n" + motivation
            
            return full_report
            
        except Exception as e:
            logger.error(f"Error generating report for {chat_id}: {e}")
            return f"❌ Error generating your weekly report. Please try again later."
    
    def generate_motivation(self, stats, user_name):
        """Generate personalized motivation based on user progress"""
        motivation = "🌟 **Personal Motivation**\n"
        motivation += "=" * 25 + "\n\n"
        
        # Streak motivation
        streak = stats['daily_streak']
        if streak >= 14:
            motivation += f"🔥 **Outstanding, {user_name}!** {streak} days of consistent learning!\n"
        elif streak >= 7:
            motivation += f"🎯 **Excellent consistency, {user_name}!** {streak}-day streak!\n"
        elif streak >= 3:
            motivation += f"👍 **Good momentum, {user_name}!** Keep building that streak!\n"
        else:
            motivation += f"💪 **Every day counts, {user_name}!** Try for daily consistency!\n"
        
        # Progress motivation
        total_words = stats['total_words_learned']
        current_level = stats['current_level']
        
        if total_words >= 100:
            motivation += "🎓 **Impressive vocabulary growth!** You're making real progress.\n"
        elif total_words >= 50:
            motivation += "📚 **Solid foundation!** Your German vocabulary is expanding.\n"
        elif total_words >= 20:
            motivation += "🌱 **Great progress!** You're building a strong base.\n"
        else:
            motivation += "🚀 **Excellent start!** Every word learned is progress.\n"
        
        # Level-specific encouragement
        motivation += f"\n🎯 **{current_level} Level Goals:**\n"
        if current_level == 'A1':
            motivation += "• Master everyday expressions and basic phrases\n"
            motivation += "• Build confidence with greetings and simple conversations\n"
        elif current_level == 'A2':
            motivation += "• Handle routine tasks and familiar topics\n"
            motivation += "• Express yourself in simple, direct exchanges\n"
        elif current_level == 'B1':
            motivation += "• Deal with most travel and work situations\n"
            motivation += "• Express opinions and explain plans\n"
        else:
            motivation += "• Handle complex topics and abstract concepts\n"
            motivation += "• Express yourself fluently and spontaneously\n"
        
        motivation += "\n🇩🇪 **Keep up the amazing work!** Consistency beats intensity in language learning!"
        
        return motivation
    
    def send_report_to_user(self, chat_id):
        """Send weekly report to a specific user"""
        try:
            # Generate personalized report
            report = self.generate_user_report(chat_id)
            
            # Send report
            success = self.send_message(chat_id, report)
            
            if success:
                # Update user's last report date
                user_progress = UserProgress(str(chat_id))
                user_progress.data['last_weekly_report'] = datetime.now().isoformat()
                user_progress.save_progress()
                
                user_info = self.active_users.get(str(chat_id), {})
                user_name = user_info.get('first_name', 'Unknown')
                logger.info(f"Weekly report sent successfully to {user_name} ({chat_id})")
                return True
            else:
                logger.error(f"Failed to send weekly report to {chat_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending report to {chat_id}: {e}")
            return False
    
    def send_reports_to_all_users(self):
        """Send weekly reports to all active users"""
        if not self.active_users:
            logger.info("No active users found")
            return True
        
        success_count = 0
        total_users = len([u for u in self.active_users.values() if u.get('active', True)])
        
        logger.info(f"Sending weekly reports to {total_users} active users")
        
        for chat_id, user_info in self.active_users.items():
            if not user_info.get('active', True):
                continue
            
            if self.send_report_to_user(chat_id):
                success_count += 1
        
        logger.info(f"Weekly reports completed: {success_count}/{total_users} successful")
        return success_count > 0 or total_users == 0
    
    def run(self):
        """Main execution method"""
        try:
            logger.info("Starting multi-user weekly reports session")
            
            if not ENHANCED_MODE:
                logger.error("Enhanced mode required for weekly reports")
                return False
            
            success = self.send_reports_to_all_users()
            
            if success:
                logger.info("Multi-user weekly reports session completed successfully")
            else:
                logger.error("Multi-user weekly reports session failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in multi-user reports execution: {e}")
            return False

def main():
    """Entry point for multi-user weekly reports"""
    try:
        reports_bot = MultiUserReportsBot()
        success = reports_bot.run()
        
        if success:
            print("✅ Multi-user weekly reports completed successfully")
        else:
            print("❌ Multi-user weekly reports failed")
        
        return success
        
    except Exception as e:
        logger.error(f"Fatal error in multi-user reports bot: {e}")
        print(f"❌ Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
