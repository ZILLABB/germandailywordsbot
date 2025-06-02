#!/usr/bin/env python3
"""
Multi-User Quiz System for German Learning Bot
Sends quizzes to all registered users
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
    from quiz_system import QuizSystem
    ENHANCED_MODE = True
except ImportError:
    ENHANCED_MODE = False
    print("Enhanced modules not available. Quiz system requires enhanced mode.")
    exit(1)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_user_quiz.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MultiUserQuizBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.vocabulary_manager = VocabularyManager()
        
        # Load active users
        self.active_users = self.load_active_users()
        
        logger.info(f"Multi-user quiz bot initialized for {len(self.active_users)} users")
    
    def load_active_users(self):
        """Load list of active users"""
        try:
            with open('active_users.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("No active_users.json found - no users to send quizzes to")
            return {}
    
    def send_message(self, chat_id, message):
        """Send message to specific user"""
        url = f"{self.api_url}/sendMessage"
        
        # Split long messages if needed
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
        for msg in messages:
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
                else:
                    logger.error(f"Telegram API error for {chat_id}: {data.get('description', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Error sending message to {chat_id}: {e}")
        
        return success_count == len(messages)
    
    def send_quiz_to_user(self, chat_id):
        """Send quiz to a specific user"""
        try:
            user_progress = UserProgress(str(chat_id), self.vocabulary_manager)
            quiz_system = QuizSystem(self.vocabulary_manager, user_progress)
            
            # Check if user should get a quiz
            if not quiz_system.should_send_quiz():
                logger.info(f"User {chat_id} not ready for quiz yet")
                return True  # Not an error, just not ready
            
            # Generate quiz
            quiz_data = quiz_system.generate_quiz(word_count=5)
            
            if not quiz_data:
                logger.info(f"No quiz data available for user {chat_id}")
                return True  # Not an error, just no words to quiz
            
            # Format quiz message
            quiz_message = quiz_system.format_quiz_message(quiz_data)
            
            # Add personalized header
            user_info = self.active_users.get(str(chat_id), {})
            user_name = user_info.get('first_name', 'there')
            
            header = f"🧠 **Quiz Time, {user_name}!**\n\n"
            header += "Test your German vocabulary knowledge:\n\n"
            
            full_message = header + quiz_message
            
            # Send quiz
            success = self.send_message(chat_id, full_message)
            
            if success:
                # Save quiz data
                quiz_filename = f"quiz_{chat_id}_{datetime.now().strftime('%Y%m%d')}.json"
                try:
                    with open(quiz_filename, 'w', encoding='utf-8') as f:
                        json.dump(quiz_data, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    logger.warning(f"Could not save quiz data for {chat_id}: {e}")
                
                logger.info(f"Quiz sent successfully to user {chat_id}")
                return True
            else:
                logger.error(f"Failed to send quiz to user {chat_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error generating/sending quiz for {chat_id}: {e}")
            return False
    
    def send_spaced_repetition_to_user(self, chat_id):
        """Send spaced repetition review to a specific user"""
        try:
            user_progress = UserProgress(str(chat_id))
            review_words = user_progress.get_words_for_review()
            
            if not review_words:
                return True  # No words to review, not an error
            
            # Create review message
            user_info = self.active_users.get(str(chat_id), {})
            user_name = user_info.get('first_name', 'there')
            
            message = f"🔄 **Review Time, {user_name}!**\n\n"
            message += f"📚 {len(review_words)} words due for review:\n\n"
            
            for i, word in enumerate(review_words[:8], 1):  # Limit to 8 words
                message += f"**{i}. {word['german']}**\n"
                message += f"🇺🇸 {word['english']}\n"
                message += f"🔊 {word['pronunciation']}\n"
                message += f"📝 {word['example']}\n\n"
            
            if len(review_words) > 8:
                message += f"... and {len(review_words) - 8} more words\n\n"
            
            message += "🎯 **Review these words to strengthen your memory!**\n"
            message += "📈 Regular review is key to long-term retention."
            
            success = self.send_message(chat_id, message)
            
            if success:
                logger.info(f"Spaced repetition sent to user {chat_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending spaced repetition to {chat_id}: {e}")
            return False
    
    def send_quizzes_to_all_users(self):
        """Send quizzes to all active users"""
        if not self.active_users:
            logger.info("No active users found")
            return True
        
        quiz_sent = 0
        review_sent = 0
        total_users = len([u for u in self.active_users.values() if u.get('active', True)])
        
        logger.info(f"Sending quizzes/reviews to {total_users} active users")
        
        for chat_id, user_info in self.active_users.items():
            if not user_info.get('active', True):
                continue
            
            user_name = user_info.get('first_name', 'Unknown')
            
            # Try to send quiz first
            if self.send_quiz_to_user(chat_id):
                quiz_sent += 1
                logger.info(f"Quiz processed for {user_name} ({chat_id})")
            
            # Also try spaced repetition
            if self.send_spaced_repetition_to_user(chat_id):
                review_sent += 1
        
        logger.info(f"Quiz session completed: {quiz_sent} quizzes, {review_sent} reviews sent to {total_users} users")
        return True
    
    def run(self):
        """Main execution method"""
        try:
            logger.info("Starting multi-user quiz session")
            
            if not ENHANCED_MODE:
                logger.error("Enhanced mode required for quiz system")
                return False
            
            success = self.send_quizzes_to_all_users()
            
            if success:
                logger.info("Multi-user quiz session completed successfully")
            else:
                logger.error("Multi-user quiz session failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in multi-user quiz execution: {e}")
            return False

def main():
    """Entry point for multi-user quiz system"""
    try:
        quiz_bot = MultiUserQuizBot()
        success = quiz_bot.run()
        
        if success:
            print("✅ Multi-user quiz session completed successfully")
        else:
            print("❌ Multi-user quiz session failed")
        
        return success
        
    except Exception as e:
        logger.error(f"Fatal error in multi-user quiz bot: {e}")
        print(f"❌ Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
