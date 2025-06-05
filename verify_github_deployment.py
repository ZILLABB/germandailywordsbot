#!/usr/bin/env python3
"""
GitHub Deployment Verification Script
Verifies that the German Daily Words Bot is properly deployed and configured
"""

import os
import json
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubDeploymentVerifier:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def verify_bot_connection(self):
        """Verify bot can connect to Telegram API"""
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=10)
            data = response.json()
            
            if data['ok']:
                bot_info = data['result']
                logger.info(f"✅ Bot connected: @{bot_info['username']}")
                logger.info(f"   Bot Name: {bot_info['first_name']}")
                logger.info(f"   Bot ID: {bot_info['id']}")
                return True
            else:
                logger.error(f"❌ Bot connection failed: {data}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error connecting to bot: {e}")
            return False
    
    def verify_github_actions_files(self):
        """Verify GitHub Actions workflow files exist"""
        workflow_file = ".github/workflows/daily_word.yml"
        
        if os.path.exists(workflow_file):
            logger.info(f"✅ GitHub Actions workflow found: {workflow_file}")
            
            # Check workflow content
            with open(workflow_file, 'r') as f:
                content = f.read()
                
            if 'cron: \'0 9 * * *\'' in content:
                logger.info("✅ Daily schedule configured (9:00 AM UTC)")
            else:
                logger.warning("⚠️  Daily schedule not found in workflow")
                
            if 'python multi_user_bot.py' in content:
                logger.info("✅ Multi-user bot execution configured")
            else:
                logger.warning("⚠️  Multi-user bot execution not found")
                
            return True
        else:
            logger.error(f"❌ GitHub Actions workflow not found: {workflow_file}")
            return False
    
    def verify_bot_files(self):
        """Verify all required bot files exist"""
        required_files = [
            'multi_user_bot.py',
            'handle_new_users.py',
            'vocabulary_manager.py',
            'user_progress.py',
            'words.json',
            'requirements.txt'
        ]
        
        missing_files = []
        for file in required_files:
            if os.path.exists(file):
                logger.info(f"✅ Required file found: {file}")
            else:
                logger.error(f"❌ Missing required file: {file}")
                missing_files.append(file)
        
        return len(missing_files) == 0
    
    def verify_user_database(self):
        """Verify user database structure"""
        if os.path.exists('active_users.json'):
            try:
                with open('active_users.json', 'r') as f:
                    users = json.load(f)
                
                logger.info(f"✅ User database found with {len(users)} users")
                return True
            except Exception as e:
                logger.error(f"❌ Error reading user database: {e}")
                return False
        else:
            logger.info("ℹ️  User database will be created when first user registers")
            return True
    
    def test_workflow_components(self):
        """Test individual workflow components"""
        logger.info("🧪 Testing workflow components...")
        
        # Test user registration handler
        try:
            from handle_new_users import UserRegistrationHandler
            handler = UserRegistrationHandler()
            logger.info("✅ User registration handler: OK")
        except Exception as e:
            logger.error(f"❌ User registration handler failed: {e}")
            return False
        
        # Test multi-user bot
        try:
            from multi_user_bot import MultiUserGermanBot
            bot = MultiUserGermanBot()
            logger.info("✅ Multi-user bot: OK")
        except Exception as e:
            logger.error(f"❌ Multi-user bot failed: {e}")
            return False
        
        # Test vocabulary manager
        try:
            from vocabulary_manager import VocabularyManager
            vocab = VocabularyManager()
            word_count = len(vocab.words)
            logger.info(f"✅ Vocabulary manager: OK ({word_count} words loaded)")
        except Exception as e:
            logger.error(f"❌ Vocabulary manager failed: {e}")
            return False
        
        return True
    
    def generate_deployment_report(self):
        """Generate comprehensive deployment report"""
        logger.info("=" * 60)
        logger.info("🚀 GITHUB DEPLOYMENT VERIFICATION REPORT")
        logger.info("=" * 60)
        
        results = {
            'bot_connection': self.verify_bot_connection(),
            'github_actions': self.verify_github_actions_files(),
            'bot_files': self.verify_bot_files(),
            'user_database': self.verify_user_database(),
            'workflow_components': self.test_workflow_components()
        }
        
        logger.info("\n📊 VERIFICATION RESULTS:")
        logger.info("-" * 40)
        
        passed = 0
        total = len(results)
        
        for test, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        logger.info("-" * 40)
        logger.info(f"OVERALL: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 DEPLOYMENT VERIFICATION: SUCCESS!")
            logger.info("🤖 Bot is ready for production!")
            logger.info("🔗 Bot Link: https://t.me/Germandailywordbot")
            logger.info("⏰ Daily lessons will run at 9:00 AM UTC")
        else:
            logger.error("⚠️  DEPLOYMENT VERIFICATION: ISSUES FOUND")
            logger.error("Please fix the failed tests before going live")
        
        return passed == total

def main():
    """Main verification function"""
    try:
        verifier = GitHubDeploymentVerifier()
        success = verifier.generate_deployment_report()
        return success
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
