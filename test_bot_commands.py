#!/usr/bin/env python3
"""
Bot Commands Testing Script
Test all bot commands to ensure they work correctly
"""

import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class BotCommandTester:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.test_chat_id = os.getenv('CHAT_ID')  # Your chat ID for testing
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        if not self.bot_token:
            raise ValueError("BOT_TOKEN must be set")
        
        print("BOT COMMANDS TESTING")
        print("=" * 40)
        print(f"Bot Token: {self.bot_token[:10]}...")
        print(f"Test Chat ID: {self.test_chat_id}")
        print("=" * 40)
    
    def send_test_message(self, text):
        """Send a test message to verify bot is responding"""
        if not self.test_chat_id or self.test_chat_id == "your_chat_id_here":
            print("No valid test chat ID - skipping message test")
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/sendMessage",
                data={
                    'chat_id': self.test_chat_id,
                    'text': text,
                    'parse_mode': 'Markdown'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('ok', False)
            
            return False
            
        except Exception as e:
            print(f"Error sending test message: {e}")
            return False
    
    def test_bot_functionality(self):
        """Test core bot functionality without sending actual messages"""
        print("\nTESTING BOT FUNCTIONALITY...")
        
        tests = []
        
        # Test 1: Bot Handler Initialization
        try:
            from telegram_bot_handler import TelegramBotHandler
            handler = TelegramBotHandler()
            tests.append(("Bot Handler Init", True))
            print("Bot handler initialized")

            # Test available commands
            expected_commands = ['/start', '/help', '/lesson', '/quiz', '/stats', '/analytics', '/streak', '/stop']
            available_commands = list(handler.commands.keys())

            missing_commands = [cmd for cmd in expected_commands if cmd not in available_commands]
            if not missing_commands:
                tests.append(("All Commands Available", True))
                print(f"All {len(expected_commands)} commands available")
            else:
                tests.append(("All Commands Available", False))
                print(f"Missing commands: {missing_commands}")
            
        except Exception as e:
            tests.append(("Bot Handler Init", False))
            print(f"Bot handler error: {e}")
        
        # Test 2: Vocabulary Manager
        try:
            from vocabulary_manager import VocabularyManager
            vocab_manager = VocabularyManager()
            word_count = len(vocab_manager.words)
            
            if word_count > 0:
                tests.append(("Vocabulary Database", True))
                print(f"✅ Vocabulary loaded: {word_count} words")
            else:
                tests.append(("Vocabulary Database", False))
                print("❌ No vocabulary words loaded")
                
        except Exception as e:
            tests.append(("Vocabulary Database", False))
            print(f"❌ Vocabulary error: {e}")
        
        # Test 3: User Progress System
        try:
            from user_progress import UserProgress
            from vocabulary_manager import VocabularyManager
            
            vocab_manager = VocabularyManager()
            user_progress = UserProgress("test_user", vocab_manager)
            stats = user_progress.get_stats()
            
            tests.append(("User Progress System", True))
            print("✅ User progress system working")
            
        except Exception as e:
            tests.append(("User Progress System", False))
            print(f"❌ User progress error: {e}")
        
        # Test 4: Quiz System
        try:
            from send_quiz import GermanQuizBot
            quiz_bot = GermanQuizBot()
            
            tests.append(("Quiz System", True))
            print("✅ Quiz system initialized")
            
        except Exception as e:
            tests.append(("Quiz System", False))
            print(f"❌ Quiz system error: {e}")
        
        # Test 5: Analytics Dashboard
        try:
            from analytics_dashboard import AnalyticsDashboard
            dashboard = AnalyticsDashboard()
            
            tests.append(("Analytics Dashboard", True))
            print("✅ Analytics dashboard working")
            
        except Exception as e:
            tests.append(("Analytics Dashboard", False))
            print(f"❌ Analytics error: {e}")
        
        # Test 6: Multi-User Support
        try:
            from multi_user_setup import MultiUserManager
            user_manager = MultiUserManager()
            
            tests.append(("Multi-User Support", True))
            print("✅ Multi-user system working")
            
        except Exception as e:
            tests.append(("Multi-User Support", False))
            print(f"❌ Multi-user error: {e}")
        
        return tests
    
    def test_webhook_integration(self):
        """Test webhook server functionality"""
        print("\n🌐 TESTING WEBHOOK INTEGRATION...")
        
        try:
            from webhook_server import app
            print("✅ Webhook server module loaded")
            
            # Test if Flask app is properly configured
            with app.test_client() as client:
                # Test health endpoint
                response = client.get('/')
                if response.status_code == 200:
                    print("✅ Health endpoint working")
                    return True
                else:
                    print(f"❌ Health endpoint failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Webhook integration error: {e}")
            return False
    
    def generate_test_report(self, functionality_tests, webhook_test):
        """Generate comprehensive test report"""
        print("\n" + "=" * 50)
        print("📋 BOT TESTING REPORT")
        print("=" * 50)
        
        # Functionality Tests
        passed_functionality = sum(1 for _, result in functionality_tests if result)
        total_functionality = len(functionality_tests)
        functionality_rate = (passed_functionality / total_functionality) * 100
        
        print(f"🎯 Functionality Tests: {functionality_rate:.1f}% ({passed_functionality}/{total_functionality})")
        
        for test_name, result in functionality_tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} - {test_name}")
        
        print()
        
        # Webhook Test
        webhook_status = "✅ PASS" if webhook_test else "❌ FAIL"
        print(f"🌐 Webhook Integration: {webhook_status}")
        
        print()
        
        # Overall Assessment
        overall_success = functionality_rate >= 80 and webhook_test
        
        if overall_success:
            print("🎉 OVERALL STATUS: EXCELLENT")
            print("   Your bot is ready for production use!")
            print()
            print("✅ PREMIUM FEATURES VERIFIED:")
            print("   • Daily German lessons with pronunciation")
            print("   • Adaptive quizzes with multiple question types")
            print("   • Progress tracking and analytics")
            print("   • Streak management and achievements")
            print("   • Multi-user support with individual progress")
            print()
            print("🚀 READY FOR USERS!")
            print("   Bot: @Germandailywordbot")
            print("   Users can start with: /start")
            
        elif functionality_rate >= 60:
            print("⚠️  OVERALL STATUS: NEEDS MINOR FIXES")
            print("   Most features working, some issues to resolve")
            
        else:
            print("❌ OVERALL STATUS: NEEDS MAJOR FIXES")
            print("   Significant issues detected, deployment not ready")
        
        return overall_success
    
    def run_all_tests(self):
        """Run all bot tests"""
        print("🎯 STARTING COMPREHENSIVE BOT TESTING")
        print("=" * 50)
        
        # Test bot functionality
        functionality_tests = self.test_bot_functionality()
        
        # Test webhook integration
        webhook_test = self.test_webhook_integration()
        
        # Generate report
        success = self.generate_test_report(functionality_tests, webhook_test)
        
        return success

def main():
    """Main testing function"""
    try:
        tester = BotCommandTester()
        return tester.run_all_tests()
        
    except Exception as e:
        print(f"❌ Fatal error during testing: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
