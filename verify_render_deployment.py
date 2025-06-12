#!/usr/bin/env python3
"""
Render Deployment Verification Script
Comprehensive testing of German Daily Words Bot deployment on Render
"""

import os
import json
import time
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class RenderDeploymentVerifier:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.webhook_url = None  # Will be set based on Render URL
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        if not self.bot_token:
            raise ValueError("BOT_TOKEN must be set in environment variables")
        
        print("🚀 RENDER DEPLOYMENT VERIFICATION")
        print("=" * 50)
        print(f"🤖 Bot Token: {self.bot_token[:10]}...")
        print(f"📅 Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
    
    def test_bot_connection(self):
        """Test basic bot API connection"""
        print("\n🔍 TESTING BOT CONNECTION...")
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    bot_info = data['result']
                    print(f"✅ Bot connected successfully!")
                    print(f"   Bot Name: {bot_info.get('first_name')}")
                    print(f"   Username: @{bot_info.get('username')}")
                    print(f"   Bot ID: {bot_info.get('id')}")
                    return True, bot_info
            
            print(f"❌ Bot connection failed: {response.text}")
            return False, None
            
        except Exception as e:
            print(f"❌ Error testing bot connection: {e}")
            return False, None
    
    def test_webhook_server(self, render_url):
        """Test webhook server health"""
        print(f"\n🌐 TESTING WEBHOOK SERVER: {render_url}")
        try:
            # Test health endpoint
            health_response = requests.get(f"{render_url}/", timeout=10)
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                print("✅ Webhook server is running!")
                print(f"   Status: {health_data.get('status')}")
                print(f"   Message: {health_data.get('message')}")
                print(f"   Bot Available: {health_data.get('bot_available')}")
                return True
            else:
                print(f"❌ Webhook server health check failed: {health_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing webhook server: {e}")
            return False
    
    def set_webhook(self, render_url):
        """Set webhook URL for the bot"""
        print(f"\n🔗 SETTING WEBHOOK URL...")
        webhook_url = f"{render_url}/webhook"
        
        try:
            response = requests.post(
                f"{self.api_url}/setWebhook",
                data={'url': webhook_url},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    print(f"✅ Webhook set successfully!")
                    print(f"   Webhook URL: {webhook_url}")
                    self.webhook_url = webhook_url
                    return True
            
            print(f"❌ Failed to set webhook: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ Error setting webhook: {e}")
            return False
    
    def get_webhook_info(self):
        """Get current webhook information"""
        print(f"\n📡 CHECKING WEBHOOK STATUS...")
        try:
            response = requests.get(f"{self.api_url}/getWebhookInfo", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    webhook_info = data['result']
                    print("✅ Webhook information retrieved!")
                    print(f"   URL: {webhook_info.get('url', 'Not set')}")
                    print(f"   Has Custom Certificate: {webhook_info.get('has_custom_certificate', False)}")
                    print(f"   Pending Updates: {webhook_info.get('pending_update_count', 0)}")
                    print(f"   Last Error: {webhook_info.get('last_error_message', 'None')}")
                    return True, webhook_info
            
            print(f"❌ Failed to get webhook info: {response.text}")
            return False, None
            
        except Exception as e:
            print(f"❌ Error getting webhook info: {e}")
            return False, None
    
    def test_bot_modules(self):
        """Test if all bot modules can be imported"""
        print(f"\n🧩 TESTING BOT MODULES...")
        
        modules_to_test = [
            'telegram_bot_handler',
            'multi_user_setup',
            'multi_user_bot',
            'vocabulary_manager',
            'user_progress',
            'send_quiz',
            'analytics_dashboard',
            'streak_manager'
        ]
        
        successful_imports = 0
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                print(f"   ✅ {module_name}")
                successful_imports += 1
            except ImportError as e:
                print(f"   ❌ {module_name}: {e}")
        
        success_rate = (successful_imports / len(modules_to_test)) * 100
        print(f"\n📊 Module Import Success Rate: {success_rate:.1f}% ({successful_imports}/{len(modules_to_test)})")
        
        return success_rate >= 80  # 80% success rate required
    
    def test_vocabulary_database(self):
        """Test vocabulary database loading"""
        print(f"\n📚 TESTING VOCABULARY DATABASE...")
        try:
            from vocabulary_manager import VocabularyManager
            vocab_manager = VocabularyManager()
            
            word_count = len(vocab_manager.words)
            levels = vocab_manager.get_available_levels()
            
            print(f"✅ Vocabulary database loaded successfully!")
            print(f"   Total Words: {word_count}")
            print(f"   Available Levels: {', '.join(levels)}")
            
            return word_count > 0
            
        except Exception as e:
            print(f"❌ Error testing vocabulary database: {e}")
            return False
    
    def simulate_user_interaction(self):
        """Simulate a user interaction to test bot functionality"""
        print(f"\n👤 SIMULATING USER INTERACTION...")
        
        # This would require actually sending messages to the bot
        # For now, we'll test the handler initialization
        try:
            from telegram_bot_handler import TelegramBotHandler
            handler = TelegramBotHandler()
            
            print("✅ Bot handler initialized successfully!")
            print(f"   Available Commands: {len(handler.commands)}")
            print(f"   Commands: {', '.join(handler.commands.keys())}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing bot handler: {e}")
            return False
    
    def run_comprehensive_verification(self, render_url):
        """Run all verification tests"""
        print("🎯 STARTING COMPREHENSIVE DEPLOYMENT VERIFICATION")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Bot Connection
        results['bot_connection'], bot_info = self.test_bot_connection()
        
        # Test 2: Webhook Server
        results['webhook_server'] = self.test_webhook_server(render_url)
        
        # Test 3: Set Webhook
        results['webhook_setup'] = self.set_webhook(render_url)
        
        # Test 4: Webhook Info
        results['webhook_info'], webhook_data = self.get_webhook_info()
        
        # Test 5: Bot Modules
        results['bot_modules'] = self.test_bot_modules()
        
        # Test 6: Vocabulary Database
        results['vocabulary_db'] = self.test_vocabulary_database()
        
        # Test 7: User Interaction Simulation
        results['user_interaction'] = self.simulate_user_interaction()
        
        # Generate Report
        self.generate_verification_report(results, bot_info, webhook_data)
        
        return results
    
    def generate_verification_report(self, results, bot_info, webhook_data):
        """Generate comprehensive verification report"""
        print("\n" + "=" * 60)
        print("📋 DEPLOYMENT VERIFICATION REPORT")
        print("=" * 60)
        
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"🎯 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print()
        
        # Test Results
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} - {test_name.replace('_', ' ').title()}")
        
        print()
        
        # Deployment Status
        if success_rate >= 85:
            print("🎉 DEPLOYMENT STATUS: EXCELLENT")
            print("   Your bot is fully operational and ready for users!")
        elif success_rate >= 70:
            print("⚠️  DEPLOYMENT STATUS: GOOD")
            print("   Your bot is mostly working but has some minor issues.")
        else:
            print("❌ DEPLOYMENT STATUS: NEEDS ATTENTION")
            print("   Your bot has significant issues that need to be resolved.")
        
        print()
        print("🚀 NEXT STEPS:")
        if success_rate >= 85:
            print("   1. Share your bot: @Germandailywordbot")
            print("   2. Monitor logs for any issues")
            print("   3. Test with real users")
        else:
            print("   1. Review failed tests above")
            print("   2. Check Render deployment logs")
            print("   3. Verify environment variables")
            print("   4. Re-run verification after fixes")

def main():
    """Main verification function"""
    try:
        # Get Render URL from user input
        render_url = input("Enter your Render app URL (e.g., https://your-app.onrender.com): ").strip()
        
        if not render_url:
            print("❌ Render URL is required")
            return False
        
        # Remove trailing slash
        render_url = render_url.rstrip('/')
        
        # Initialize verifier
        verifier = RenderDeploymentVerifier()
        
        # Run verification
        results = verifier.run_comprehensive_verification(render_url)
        
        # Return overall success
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        return (passed_tests / total_tests) >= 0.85
        
    except Exception as e:
        print(f"❌ Fatal error during verification: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
