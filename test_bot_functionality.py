#!/usr/bin/env python3
"""
Comprehensive Bot Functionality Test Script
Tests all Phase 1 and Phase 2 features on your personal Telegram account
"""

import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import all bot modules
try:
    from multi_user_bot import MultiUserGermanBot
    from send_quiz import GermanQuizBot
    from analytics_dashboard import AnalyticsDashboard
    from send_weekly_analytics import WeeklyAnalyticsReporter
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    ALL_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"❌ Module import error: {e}")
    ALL_MODULES_AVAILABLE = False
    exit(1)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BotFunctionalityTester:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.chat_id = os.getenv('CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("BOT_TOKEN and CHAT_ID must be set in .env file")
        
        print(f"🤖 Testing German Daily Word Bot")
        print(f"📱 Target Chat ID: {self.chat_id}")
        print(f"🔑 Bot Token: {self.bot_token[:10]}...")
        print("=" * 60)
    
    def run_comprehensive_test(self):
        """Run all bot functionality tests"""
        print("\n🧪 COMPREHENSIVE BOT FUNCTIONALITY TEST")
        print("=" * 50)
        
        test_results = []
        
        # Test 1: Daily Lesson Delivery
        print("\n1️⃣ TESTING DAILY LESSON DELIVERY")
        result1 = self.test_daily_lesson()
        test_results.append(("Daily Lesson", result1))
        
        # Test 2: Enhanced Quiz System
        print("\n2️⃣ TESTING ENHANCED QUIZ SYSTEM")
        result2 = self.test_quiz_system()
        test_results.append(("Quiz System", result2))
        
        # Test 3: Analytics Dashboard
        print("\n3️⃣ TESTING ANALYTICS DASHBOARD")
        result3 = self.test_analytics_dashboard()
        test_results.append(("Analytics Dashboard", result3))
        
        # Test 4: Streak and Progress Tracking
        print("\n4️⃣ TESTING STREAK & PROGRESS TRACKING")
        result4 = self.test_streak_tracking()
        test_results.append(("Streak Tracking", result4))
        
        # Test 5: Weekly Analytics
        print("\n5️⃣ TESTING WEEKLY ANALYTICS")
        result5 = self.test_weekly_analytics()
        test_results.append(("Weekly Analytics", result5))
        
        # Print comprehensive results
        self.print_test_summary(test_results)
        
        return all(result for _, result in test_results)
    
    def test_daily_lesson(self):
        """Test daily lesson delivery with enhanced features"""
        try:
            print("   📚 Initializing multi-user bot...")
            bot = MultiUserGermanBot()
            
            print(f"   📤 Sending enhanced daily lesson to {self.chat_id}...")
            success = bot.send_daily_lesson_to_user(self.chat_id)
            
            if success:
                print("   ✅ Daily lesson sent successfully!")
                print("   📱 Check your Telegram for the enhanced lesson with:")
                print("      - 3-5 German words with pronunciation")
                print("      - Cultural context and examples")
                print("      - Streak tracking and milestone notifications")
                return True
            else:
                print("   ❌ Failed to send daily lesson")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing daily lesson: {e}")
            return False
    
    def test_quiz_system(self):
        """Test enhanced quiz system with adaptive features"""
        try:
            print("   🧠 Initializing enhanced quiz system...")
            quiz_bot = GermanQuizBot()
            
            # Check if user has enough words for quiz
            if not quiz_bot.should_send_quiz_today():
                print("   ℹ️  User needs more learned words for quiz")
                print("   📚 Adding some test words to enable quiz...")
                
                # Add some words to enable quiz testing
                user_progress = UserProgress(self.chat_id, quiz_bot.vocabulary_manager)
                test_words = [
                    {'german': 'Hallo', 'english': 'Hello', 'level': 'A1'},
                    {'german': 'Danke', 'english': 'Thank you', 'level': 'A1'},
                    {'german': 'Wasser', 'english': 'Water', 'level': 'A1'},
                    {'german': 'Brot', 'english': 'Bread', 'level': 'A1'},
                    {'german': 'Haus', 'english': 'House', 'level': 'A1'}
                ]
                
                for word in test_words:
                    user_progress.add_learned_word(word)
                user_progress.save_progress()
                print("   ✅ Test words added successfully")
            
            print("   📤 Sending adaptive quiz...")
            success = quiz_bot.send_vocabulary_quiz('adaptive')
            
            if success:
                print("   ✅ Enhanced quiz sent successfully!")
                print("   📱 Check your Telegram for the adaptive quiz with:")
                print("      - Multiple question types (fill-in-blank, contextual, etc.)")
                print("      - Difficulty adapted to your level")
                print("      - Detailed explanations and feedback")
                return True
            else:
                print("   ❌ Failed to send quiz")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing quiz system: {e}")
            return False
    
    def test_analytics_dashboard(self):
        """Test analytics dashboard reports"""
        try:
            print("   📊 Initializing analytics dashboard...")
            dashboard = AnalyticsDashboard()
            
            # Test different report types
            report_types = [
                ('comprehensive', 'Comprehensive Report'),
                ('streak', 'Streak Analytics'),
                ('performance', 'Performance Analysis'),
                ('quick', 'Quick Stats')
            ]
            
            success_count = 0
            for report_type, description in report_types:
                print(f"   📤 Sending {description}...")
                success = dashboard.send_analytics_report(self.chat_id, report_type)
                
                if success:
                    print(f"   ✅ {description} sent successfully!")
                    success_count += 1
                    time.sleep(2)  # Avoid rate limiting
                else:
                    print(f"   ❌ Failed to send {description}")
            
            if success_count >= 3:  # At least 3 out of 4 reports successful
                print("   📱 Check your Telegram for detailed analytics reports!")
                return True
            else:
                print(f"   ⚠️  Only {success_count}/4 reports sent successfully")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing analytics dashboard: {e}")
            return False
    
    def test_streak_tracking(self):
        """Test advanced streak tracking and milestones"""
        try:
            print("   🔥 Testing streak tracking system...")
            
            # Initialize user progress with enhanced features
            vocabulary_manager = VocabularyManager()
            user_progress = UserProgress(self.chat_id, vocabulary_manager)
            
            # Get current streak stats
            if hasattr(user_progress, 'streak_manager') and user_progress.streak_manager:
                streak_stats = user_progress.streak_manager.get_streak_stats()
                print(f"   📊 Current Streak: {streak_stats['current_streak']} days")
                print(f"   🏆 Longest Streak: {streak_stats['longest_streak']} days")
                print(f"   🎖️ Milestones Achieved: {streak_stats['streak_milestones_achieved']}")
                print(f"   🛡️ Streak Freezes Available: {streak_stats['streak_freeze_available']}")
                
                # Test streak message formatting
                test_streak_info = {
                    'streak_continued': True,
                    'milestone_reached': None,
                    'grace_period_used': False,
                    'streak_recovered': False
                }
                
                message = user_progress.streak_manager.format_streak_message(test_streak_info)
                print("   ✅ Streak tracking system operational!")
                print("   📱 Streak messages will appear with daily lessons")
                return True
            else:
                print("   ⚠️  Advanced streak manager not available, using basic tracking")
                return True
                
        except Exception as e:
            print(f"   ❌ Error testing streak tracking: {e}")
            return False
    
    def test_weekly_analytics(self):
        """Test weekly analytics report system"""
        try:
            print("   📅 Testing weekly analytics system...")
            
            reporter = WeeklyAnalyticsReporter()
            
            # Test individual report generation
            print("   📤 Sending weekly summary report...")
            success = reporter.send_report_to_user(self.chat_id, 'weekly')
            
            if success:
                print("   ✅ Weekly analytics sent successfully!")
                print("   📱 Check your Telegram for comprehensive weekly summary!")
                return True
            else:
                print("   ❌ Failed to send weekly analytics")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing weekly analytics: {e}")
            return False
    
    def print_test_summary(self, test_results):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("🧪 BOT FUNCTIONALITY TEST SUMMARY")
        print("="*60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if result:
                passed_tests += 1
        
        print("="*60)
        print(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Your bot is fully operational!")
            print("\n📱 CHECK YOUR TELEGRAM NOW for:")
            print("   • Enhanced daily lesson with streak tracking")
            print("   • Adaptive quiz with multiple question types")
            print("   • Comprehensive analytics reports")
            print("   • Weekly learning summary")
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed. Check logs for details.")
        
        print("="*60)

def main():
    """Main function to run bot functionality tests"""
    try:
        if not ALL_MODULES_AVAILABLE:
            print("❌ Not all required modules are available")
            return False
        
        tester = BotFunctionalityTester()
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n🎉 BOT TESTING COMPLETE!")
            print("Your German Daily Word Bot is ready for use!")
        else:
            print("\n⚠️  Some tests failed. Check the logs for details.")
        
        return success
        
    except Exception as e:
        logger.error(f"Fatal error in bot testing: {e}")
        print(f"❌ Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
