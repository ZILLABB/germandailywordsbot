#!/usr/bin/env python3
"""
Deployment Verification Script for German Learning System
Verifies all components are working correctly
"""

import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Check environment variables"""
    print("🔧 Checking Environment Configuration...")
    
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    
    if not bot_token:
        print("❌ BOT_TOKEN not found in environment")
        return False
    else:
        print(f"✅ BOT_TOKEN configured (ends with: ...{bot_token[-10:]})")
    
    if not chat_id:
        print("❌ CHAT_ID not found in environment")
        return False
    else:
        print(f"✅ CHAT_ID configured: {chat_id}")
    
    return True

def check_vocabulary_database():
    """Check vocabulary database"""
    print("\n📚 Checking Vocabulary Database...")
    
    try:
        with open('words.json', 'r', encoding='utf-8') as f:
            words = json.load(f)
        
        print(f"✅ Vocabulary database loaded: {len(words)} words")
        
        # Check structure
        required_fields = ['german', 'english', 'pronunciation', 'example', 'example_translation', 'category']
        enhanced_fields = ['level', 'frequency', 'word_type', 'grammar_info', 'cultural_note']
        
        enhanced_count = 0
        for word in words[:5]:  # Check first 5 words
            missing_fields = [field for field in required_fields if field not in word]
            if missing_fields:
                print(f"⚠️  Word '{word.get('german', 'unknown')}' missing: {missing_fields}")
            
            enhanced_present = [field for field in enhanced_fields if field in word]
            if len(enhanced_present) >= 3:
                enhanced_count += 1
        
        if enhanced_count >= 3:
            print("✅ Enhanced vocabulary structure detected")
        else:
            print("⚠️  Basic vocabulary structure (enhanced features may be limited)")
        
        return True
        
    except FileNotFoundError:
        print("❌ words.json not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in words.json: {e}")
        return False

def check_enhanced_modules():
    """Check if enhanced modules are available"""
    print("\n🧠 Checking Enhanced Learning Modules...")
    
    modules = [
        ('user_progress.py', 'User Progress Tracking'),
        ('vocabulary_manager.py', 'Smart Vocabulary Management'),
        ('quiz_system.py', 'Interactive Quiz System'),
        ('progress_stats.py', 'Advanced Analytics'),
        ('send_quiz.py', 'Quiz Bot'),
        ('send_weekly_report.py', 'Weekly Report Bot')
    ]
    
    available_modules = 0
    for module_file, description in modules:
        if os.path.exists(module_file):
            print(f"✅ {description}: {module_file}")
            available_modules += 1
        else:
            print(f"❌ {description}: {module_file} not found")
    
    if available_modules == len(modules):
        print("🎉 All enhanced modules available - Full learning system active!")
        return True
    elif available_modules >= 4:
        print("⚠️  Most enhanced modules available - Partial functionality")
        return True
    else:
        print("❌ Enhanced modules missing - Basic mode only")
        return False

def test_basic_functionality():
    """Test basic bot functionality"""
    print("\n🧪 Testing Basic Functionality...")
    
    try:
        # Test imports
        if check_enhanced_modules():
            from user_progress import UserProgress
            from vocabulary_manager import VocabularyManager
            
            # Test user progress
            progress = UserProgress("test_user")
            print("✅ User progress system working")
            
            # Test vocabulary manager
            vocab_manager = VocabularyManager()
            print(f"✅ Vocabulary manager loaded {len(vocab_manager.words)} words")
            
            # Test word selection
            test_words = vocab_manager.get_words_for_level('A1', 3)
            if test_words:
                print(f"✅ Word selection working: {len(test_words)} words selected")
            else:
                print("⚠️  Word selection returned no results")
            
            # Clean up test file
            test_file = "progress_test_user.json"
            if os.path.exists(test_file):
                os.remove(test_file)
        
        return True
        
    except ImportError as e:
        print(f"⚠️  Enhanced modules not available: {e}")
        print("📝 Bot will run in basic mode")
        return True
    except Exception as e:
        print(f"❌ Error testing functionality: {e}")
        return False

def check_github_workflow():
    """Check GitHub Actions workflow"""
    print("\n🤖 Checking GitHub Actions Workflow...")
    
    workflow_file = '.github/workflows/daily_word.yml'
    if os.path.exists(workflow_file):
        print("✅ GitHub Actions workflow file found")
        
        try:
            with open(workflow_file, 'r') as f:
                content = f.read()
            
            # Check for enhanced features
            if 'send_quiz.py' in content:
                print("✅ Quiz automation configured")
            if 'send_weekly_report.py' in content:
                print("✅ Weekly report automation configured")
            if 'cron:' in content:
                cron_count = content.count('cron:')
                print(f"✅ {cron_count} scheduled jobs configured")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Could not read workflow file: {e}")
            return False
    else:
        print("❌ GitHub Actions workflow not found")
        return False

def generate_deployment_report():
    """Generate comprehensive deployment report"""
    print("\n" + "="*60)
    print("📊 DEPLOYMENT VERIFICATION REPORT")
    print("="*60)
    
    checks = [
        ("Environment Configuration", check_environment()),
        ("Vocabulary Database", check_vocabulary_database()),
        ("Enhanced Modules", check_enhanced_modules()),
        ("Basic Functionality", test_basic_functionality()),
        ("GitHub Workflow", check_github_workflow())
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    print(f"\n📈 Overall Status: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 DEPLOYMENT SUCCESSFUL - All systems operational!")
        print("\n🚀 Your German Learning System is ready for:")
        print("   📚 Daily personalized vocabulary lessons")
        print("   🧠 Interactive quizzes and spaced repetition")
        print("   📊 Weekly progress reports and analytics")
        print("   🎯 CEFR level progression (A1→B2)")
        print("   🤖 Fully automated GitHub Actions delivery")
        
        print("\n📋 Next Steps:")
        print("   1. Verify GitHub repository secrets are set:")
        print("      - BOT_TOKEN (your Telegram bot token)")
        print("      - CHAT_ID (your Telegram chat ID)")
        print("   2. Check GitHub Actions tab for automated runs")
        print("   3. Monitor your Telegram for daily lessons!")
        
        return True
    else:
        print("⚠️  DEPLOYMENT INCOMPLETE - Some issues detected")
        print("\n🔧 Issues to resolve:")
        for name, result in checks:
            if not result:
                print(f"   ❌ {name}")
        
        return False

def main():
    """Main verification function"""
    print("🇩🇪 German Learning System - Deployment Verification")
    print("=" * 60)
    print(f"📅 Verification Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = generate_deployment_report()
    
    if success:
        print("\n✅ Verification completed successfully!")
        return 0
    else:
        print("\n❌ Verification found issues that need attention.")
        return 1

if __name__ == "__main__":
    exit(main())
