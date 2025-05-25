#!/usr/bin/env python3
"""
German Learning Weekly Report Bot
Sends comprehensive weekly progress reports and analytics
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import our enhanced modules
try:
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    from progress_stats import ProgressAnalytics
    ENHANCED_MODE = True
except ImportError:
    ENHANCED_MODE = False
    print("Enhanced modules not available. Weekly reports require enhanced mode.")
    exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weekly_report.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class WeeklyReportBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.chat_id = os.getenv('CHAT_ID')
        
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        if not self.chat_id:
            raise ValueError("CHAT_ID environment variable is required")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Initialize systems
        self.user_progress = UserProgress(self.chat_id)
        self.vocabulary_manager = VocabularyManager()
        self.analytics = ProgressAnalytics(self.chat_id)
        
        logger.info(f"Weekly report bot initialized for user {self.chat_id}")
    
    def should_send_weekly_report(self) -> bool:
        """Check if weekly report should be sent (every Sunday)"""
        today = datetime.now()
        return today.weekday() == 6  # Sunday = 6
    
    def send_message(self, message):
        """Send message via Telegram Bot API"""
        url = f"{self.api_url}/sendMessage"
        
        # Split long messages if needed
        max_length = 4000  # Telegram limit is 4096, leave some buffer
        
        if len(message) <= max_length:
            messages = [message]
        else:
            # Split message at logical points
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
                'chat_id': self.chat_id,
                'text': msg,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            
            try:
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if data['ok']:
                    logger.info(f"Message part {i+1}/{len(messages)} sent successfully")
                    success_count += 1
                else:
                    logger.error(f"Telegram API error for part {i+1}: {data.get('description', 'Unknown error')}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error sending message part {i+1}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error sending message part {i+1}: {e}")
        
        return success_count == len(messages)
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive weekly learning report"""
        try:
            # Get basic weekly report
            weekly_report = self.analytics.generate_weekly_report()
            
            # Get learning insights
            insights = self.analytics.generate_learning_insights()
            
            # Add motivational section
            stats = self.user_progress.get_stats()
            
            motivation_section = "\n🌟 **Motivation & Goals**\n"
            motivation_section += "=" * 30 + "\n\n"
            
            # Personalized motivation based on progress
            if stats['daily_streak'] >= 7:
                motivation_section += "🔥 **Amazing consistency!** You're building a strong learning habit.\n"
            elif stats['daily_streak'] >= 3:
                motivation_section += "👍 **Good momentum!** Keep up the daily practice.\n"
            else:
                motivation_section += "💪 **Every day counts!** Try to build a consistent daily habit.\n"
            
            if stats['total_words_learned'] >= 50:
                motivation_section += "🎓 **Impressive vocabulary growth!** You're making real progress.\n"
            elif stats['total_words_learned'] >= 20:
                motivation_section += "📚 **Solid foundation!** Your vocabulary is expanding nicely.\n"
            else:
                motivation_section += "🌱 **Great start!** Every word learned is a step forward.\n"
            
            # Next week goals
            motivation_section += "\n🎯 **Goals for Next Week:**\n"
            current_level = stats['current_level']
            
            if current_level == 'A1':
                motivation_section += "• Master 15+ A1 vocabulary words\n"
                motivation_section += "• Focus on basic greetings and daily life terms\n"
                motivation_section += "• Practice pronunciation daily\n"
            elif current_level == 'A2':
                motivation_section += "• Learn 20+ new A2 vocabulary words\n"
                motivation_section += "• Review A1 words for retention\n"
                motivation_section += "• Start recognizing basic grammar patterns\n"
            else:
                motivation_section += f"• Continue building {current_level} vocabulary\n"
                motivation_section += "• Focus on complex grammar structures\n"
                motivation_section += "• Practice with authentic German content\n"
            
            motivation_section += "• Maintain your daily learning streak\n"
            motivation_section += "• Complete any review sessions\n\n"
            
            motivation_section += "🇩🇪 **Remember:** Consistency beats intensity in language learning!\n"
            motivation_section += "📈 **You're doing great!** Keep up the excellent work!"
            
            # Combine all sections
            complete_report = weekly_report + "\n\n" + insights + "\n\n" + motivation_section
            
            return complete_report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return f"❌ Error generating weekly report: {e}"
    
    def send_weekly_report(self):
        """Generate and send the weekly progress report"""
        try:
            logger.info("Generating weekly progress report")
            
            # Generate comprehensive report
            report = self.generate_comprehensive_report()
            
            # Add header with date
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday() + 1)  # Last Monday
            week_end = week_start + timedelta(days=6)  # Last Sunday
            
            header = f"📊 **Weekly German Learning Report**\n"
            header += f"📅 Week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}\n"
            header += "🇩🇪 Your personalized learning analytics\n\n"
            
            full_report = header + report
            
            # Send the report
            success = self.send_message(full_report)
            
            if success:
                logger.info("Weekly report sent successfully")
                
                # Update user's last report date
                self.user_progress.data['last_weekly_report'] = datetime.now().isoformat()
                self.user_progress.save_progress()
                
                return True
            else:
                logger.error("Failed to send weekly report")
                return False
                
        except Exception as e:
            logger.error(f"Error sending weekly report: {e}")
            return False
    
    def run(self):
        """Main execution method for weekly report bot"""
        try:
            logger.info("Starting Weekly Report Bot session")
            
            stats = self.user_progress.get_stats()
            logger.info(f"User stats: Level {stats['current_level']}, "
                       f"{stats['total_words_learned']} words learned")
            
            # Check if user has enough activity for a meaningful report
            if stats['total_words_learned'] < 5:
                logger.info("User has insufficient activity for weekly report")
                
                # Send encouragement message instead
                encouragement = "🌱 **Keep Learning!**\n\n"
                encouragement += "You're just getting started with your German learning journey! "
                encouragement += "Complete a few more daily lessons to unlock your first weekly progress report.\n\n"
                encouragement += "🎯 **Goal:** Learn 5+ words to get your first analytics report!\n"
                encouragement += "📚 Keep up the daily practice - you're doing great! 🇩🇪"
                
                return self.send_message(encouragement)
            
            # Send weekly report
            success = self.send_weekly_report()
            
            if success:
                logger.info("Weekly report bot session completed successfully")
            else:
                logger.error("Weekly report bot session failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in weekly report bot execution: {e}")
            return False

def main():
    """Entry point for the weekly report application"""
    try:
        if not ENHANCED_MODE:
            print("❌ Weekly reports require enhanced mode with all modules available")
            return False
        
        report_bot = WeeklyReportBot()
        success = report_bot.run()
        
        if success:
            print("✅ Weekly report session completed successfully")
        else:
            print("❌ Weekly report session failed")
        
        return success
        
    except Exception as e:
        logger.error(f"Fatal error in weekly report bot: {e}")
        print(f"❌ Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
