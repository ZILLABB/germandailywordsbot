#!/usr/bin/env python3
"""
German Daily Quiz Bot - Interactive Learning
Sends weekly quizzes and spaced repetition reviews
"""

import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import our enhanced modules
try:
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    from quiz_system import QuizSystem
    from enhanced_quiz_system import EnhancedQuizSystem
    ENHANCED_MODE = True
    ENHANCED_QUIZ_MODE = True
except ImportError:
    ENHANCED_MODE = False
    ENHANCED_QUIZ_MODE = False
    print("Enhanced modules not available. Quiz system requires enhanced mode.")
    exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quiz_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GermanQuizBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.chat_id = os.getenv('CHAT_ID')
        
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        if not self.chat_id:
            raise ValueError("CHAT_ID environment variable is required")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Initialize systems
        self.vocabulary_manager = VocabularyManager()
        self.user_progress = UserProgress(self.chat_id, self.vocabulary_manager)

        # Initialize enhanced quiz system if available
        if ENHANCED_QUIZ_MODE:
            self.enhanced_quiz = EnhancedQuizSystem(self.vocabulary_manager, self.user_progress)
        else:
            self.enhanced_quiz = None

        self.quiz_system = QuizSystem(self.vocabulary_manager, self.user_progress)
        
        logger.info(f"Quiz bot initialized for user {self.chat_id}")
    
    def should_send_quiz_today(self) -> bool:
        """Check if a quiz should be sent today"""
        if self.enhanced_quiz:
            return self.enhanced_quiz.should_send_enhanced_quiz()
        else:
            return self.quiz_system.should_send_quiz()
    
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
                logger.info(f"Quiz message sent successfully. Message ID: {data['result']['message_id']}")
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
    
    def send_vocabulary_quiz(self, quiz_type: str = 'adaptive'):
        """Send an interactive vocabulary quiz with enhanced features"""
        try:
            # Generate quiz using enhanced system if available
            if self.enhanced_quiz:
                quiz_data = self.enhanced_quiz.generate_enhanced_quiz(quiz_type, word_count=5)
                quiz_message = self.enhanced_quiz.format_enhanced_quiz_message(quiz_data)
                quiz_info = f"Enhanced quiz ({quiz_type})"
            else:
                quiz_data = self.quiz_system.generate_quiz(word_count=5)
                quiz_message = self.quiz_system.format_quiz_message(quiz_data)
                quiz_info = "Standard quiz"

            if not quiz_data:
                logger.info("No quiz data available - user needs more learned words")
                return False

            # Send quiz
            success = self.send_message(quiz_message)

            if success:
                logger.info(f"{quiz_info} sent successfully with {len(quiz_data['questions'])} questions")

                # Save quiz data for potential future processing
                quiz_filename = f"quiz_{self.chat_id}_{datetime.now().strftime('%Y%m%d')}.json"
                try:
                    import json
                    with open(quiz_filename, 'w', encoding='utf-8') as f:
                        json.dump(quiz_data, f, indent=2, ensure_ascii=False)
                    logger.info(f"Quiz data saved to {quiz_filename}")
                except Exception as e:
                    logger.warning(f"Could not save quiz data: {e}")

                return True
            else:
                logger.error("Failed to send vocabulary quiz")
                return False

        except Exception as e:
            logger.error(f"Error generating/sending quiz: {e}")
            return False
    
    def send_spaced_repetition_review(self):
        """Send words due for spaced repetition review"""
        try:
            review_words = self.user_progress.get_words_for_review()
            
            if not review_words:
                logger.info("No words due for review today")
                return True  # Not an error, just nothing to review
            
            # Create review message
            today = datetime.now().strftime('%A, %B %d, %Y')
            
            message = f"🔄 **Spaced Repetition Review**\n"
            message += f"📅 {today}\n"
            message += f"📚 {len(review_words)} words due for review\n"
            message += "=" * 40 + "\n\n"
            
            for i, word in enumerate(review_words[:10], 1):  # Limit to 10 words
                message += f"**{i}. {word['german']}**\n"
                message += f"🇺🇸 {word['english']}\n"
                message += f"🔊 {word['pronunciation']}\n"
                message += f"📝 {word['example']}\n"
                message += f"💭 _{word['example_translation']}_\n\n"
            
            if len(review_words) > 10:
                message += f"... and {len(review_words) - 10} more words\n\n"
            
            message += "🎯 **Review these words and test yourself!**\n"
            message += "📈 Regular review strengthens long-term memory."
            
            success = self.send_message(message)
            
            if success:
                logger.info(f"Spaced repetition review sent with {len(review_words)} words")
                return True
            else:
                logger.error("Failed to send spaced repetition review")
                return False
                
        except Exception as e:
            logger.error(f"Error sending spaced repetition review: {e}")
            return False
    
    def run(self):
        """Main execution method for quiz bot"""
        try:
            logger.info("Starting German Quiz Bot session")
            
            stats = self.user_progress.get_stats()
            logger.info(f"User stats: Level {stats['current_level']}, "
                       f"{stats['total_words_learned']} words learned, "
                       f"{stats['words_due_for_review']} due for review")
            
            actions_taken = []
            
            # Check if quiz should be sent
            if self.should_send_quiz_today():
                logger.info("Quiz day detected - sending vocabulary quiz")
                if self.send_vocabulary_quiz():
                    actions_taken.append("vocabulary_quiz")
            
            # Check for spaced repetition review
            if stats['words_due_for_review'] > 0:
                logger.info(f"{stats['words_due_for_review']} words due for review")
                if self.send_spaced_repetition_review():
                    actions_taken.append("spaced_repetition")
            
            if not actions_taken:
                logger.info("No quiz or review needed today")
                return True
            
            logger.info(f"Quiz bot session completed. Actions: {', '.join(actions_taken)}")
            return True
            
        except Exception as e:
            logger.error(f"Error in quiz bot execution: {e}")
            return False

def main():
    """Entry point for the quiz application"""
    try:
        if not ENHANCED_MODE:
            print("❌ Quiz system requires enhanced mode with all modules available")
            return False
        
        quiz_bot = GermanQuizBot()
        success = quiz_bot.run()
        
        if success:
            print("✅ Quiz bot session completed successfully")
        else:
            print("❌ Quiz bot session failed")
        
        return success
        
    except Exception as e:
        logger.error(f"Fatal error in quiz bot: {e}")
        print(f"❌ Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
