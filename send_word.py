#!/usr/bin/env python3
"""
German Daily Word Bot - Enhanced Progressive Learning System
Sends personalized German vocabulary lessons with CEFR level progression
"""

import os
import requests
import logging
import random
from datetime import datetime
from dotenv import load_dotenv

# Import our custom modules
try:
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    ENHANCED_MODE = True
except ImportError:
    # Fallback to basic mode if enhanced modules aren't available
    ENHANCED_MODE = False
    import json

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

        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        if not self.chat_id:
            raise ValueError("CHAT_ID environment variable is required")

        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

        if ENHANCED_MODE:
            # Initialize enhanced systems
            self.vocabulary_manager = VocabularyManager()
            self.user_progress = UserProgress(self.chat_id)

            # Get user preferences
            preferences = self.user_progress.get_preferences()
            self.words_per_day = preferences.get('words_per_day', 3)

            logger.info(f"Enhanced bot initialized for user {self.chat_id}")
            logger.info(f"User level: {self.user_progress.get_current_level()}")
            logger.info(f"Words per day: {self.words_per_day}")

            # Check for level progression
            self.check_level_progression()
        else:
            # Basic mode fallback
            self.words_per_day = int(os.getenv('WORDS_PER_DAY', '3'))
            self.words = self.load_words_basic()
            logger.info(f"Basic bot initialized with {len(self.words)} words, sending {self.words_per_day} words per day")

    def load_words_basic(self):
        """Load German vocabulary from JSON file (basic mode)"""
        try:
            import json
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

    def check_level_progression(self):
        """Check if user should level up and handle progression (enhanced mode only)"""
        if not ENHANCED_MODE:
            return None
        if self.user_progress.should_level_up():
            new_level = self.user_progress.level_up()
            if new_level:
                logger.info(f"User {self.chat_id} progressed to level {new_level}")
                return new_level
        return None

    def get_daily_words(self):
        """Get words for today - enhanced or basic mode"""
        if ENHANCED_MODE:
            return self.get_daily_words_enhanced()
        else:
            return self.get_daily_words_basic()

    def get_daily_words_enhanced(self):
        """Get personalized words based on user's level and progress (enhanced mode)"""
        user_level = self.user_progress.get_current_level()
        learned_words = []

        # Collect all learned words across levels
        for level_data in self.user_progress.data['words_by_level'].values():
            learned_words.extend(level_data['learned'])

        # Get progressive words based on user level
        selected_words = self.vocabulary_manager.get_progressive_words(
            user_level, self.words_per_day, learned_words
        )

        # Check for review words (25% chance to include review)
        if random.random() < 0.25 and learned_words:
            review_words = self.user_progress.get_words_for_review()
            if review_words:
                # Replace one new word with a review word
                if selected_words:
                    selected_words[-1] = random.choice(review_words)

        logger.info(f"Selected {len(selected_words)} words for level {user_level}")
        return selected_words

    def get_daily_words_basic(self):
        """Get words using deterministic selection (basic mode)"""
        today = datetime.now()
        # Create a seed based on the current date
        date_seed = today.year * 10000 + today.month * 100 + today.day

        # Use the date as a seed to get consistent daily selection
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
        """Format the complete daily message - enhanced or basic mode"""
        if ENHANCED_MODE:
            return self.format_daily_message_enhanced(words)
        else:
            return self.format_daily_message_basic(words)

    def format_daily_message_enhanced(self, words):
        """Format the complete daily message with enhanced learning information"""
        today = datetime.now().strftime('%A, %B %d, %Y')
        user_stats = self.user_progress.get_stats()

        # Header with personalized information
        header = f"🌅 **German Learning Journey**\n"
        header += f"📅 {today}\n"
        header += f"🎯 Level: {user_stats['current_level']} | "
        header += f"📚 Total Words: {user_stats['total_words_learned']} | "
        header += f"🔥 Streak: {user_stats['daily_streak']} days\n"
        header += f"📖 Today's lesson ({len(words)} words)\n"
        header += "=" * 50 + "\n\n"

        word_messages = []
        for i, word in enumerate(words, 1):
            # Enhanced word formatting
            level_emoji = {"A1": "🟢", "A2": "🟡", "B1": "🟠", "B2": "🔴"}
            level_indicator = level_emoji.get(word.get('level', 'A1'), '⚪')

            word_msg = f"**{i}. {word['german']}** {level_indicator} {word.get('level', 'A1')}\n"
            word_msg += f"🇺🇸 {word['english']}\n"
            word_msg += f"🔊 {word['pronunciation']}\n"

            # Add grammatical information if available
            if 'word_type' in word:
                word_msg += f"📝 {word['word_type'].title()}"
                if 'grammar_info' in word and 'formality' in word['grammar_info']:
                    word_msg += f" ({word['grammar_info']['formality']})"
                word_msg += "\n"

            word_msg += f"💬 {word['example']}\n"
            word_msg += f"💭 _{word['example_translation']}_\n"

            # Add cultural note if available
            if 'cultural_note' in word:
                word_msg += f"🌍 {word['cultural_note']}\n"

            word_messages.append(word_msg)

        # Add grammar tip
        grammar_tip = self.vocabulary_manager.get_grammar_tip(words)
        if grammar_tip:
            grammar_section = f"\n📚 **Grammar Tip:**\n{grammar_tip}\n"
        else:
            grammar_section = ""

        # Enhanced footer with progress information
        footer = "\n" + "=" * 50 + "\n"

        # Check for achievements or level up
        level_up_msg = self.check_level_progression()
        if level_up_msg:
            footer += f"🎉 **Congratulations!** You've progressed to level {level_up_msg}!\n"

        footer += "🎯 **Practice Tip:** Try using these words in your own sentences today!\n"

        # Show words due for review
        if user_stats['words_due_for_review'] > 0:
            footer += f"📝 You have {user_stats['words_due_for_review']} words due for review.\n"

        footer += "🔄 New personalized lesson tomorrow!\n"
        footer += "📈 Keep building your German vocabulary! 🇩🇪"

        complete_message = header + "\n".join(word_messages) + grammar_section + footer

        return complete_message

    def format_daily_message_basic(self, words):
        """Format the complete daily message (basic mode)"""
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
        """Main execution method - enhanced or basic mode"""
        try:
            if ENHANCED_MODE:
                logger.info("Starting enhanced German learning session")

                # Update daily streak
                self.user_progress.update_daily_streak()

                # Get today's personalized words
                daily_words = self.get_daily_words()

                if not daily_words:
                    logger.warning("No words selected for today")
                    return False

                # Format the enhanced message
                message = self.format_daily_message(daily_words)

                # Send the message
                success = self.send_message(message)

                if success:
                    # Mark words as learned and update progress
                    for word in daily_words:
                        # Ensure word has required fields for progress tracking
                        if 'level' not in word:
                            word['level'] = 'A1'  # Default level
                        self.user_progress.add_learned_word(word)

                    # Save progress
                    self.user_progress.save_progress()

                    logger.info("Enhanced German lesson sent successfully!")
                    word_list = [f"{word['german']} ({word.get('level', 'A1')})" for word in daily_words]
                    logger.info(f"Words sent: {', '.join(word_list)}")

                    # Log user stats
                    stats = self.user_progress.get_stats()
                    logger.info(f"User progress: Level {stats['current_level']}, "
                              f"{stats['total_words_learned']} total words, "
                              f"{stats['daily_streak']} day streak")
                else:
                    logger.error("Failed to send enhanced lesson")
                    return False
            else:
                # Basic mode
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
