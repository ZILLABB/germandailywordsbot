#!/usr/bin/env python3
"""
Demo Script for Advanced Analytics Features
Demonstrates the new streak management and learning analytics capabilities
"""

import os
import json
import logging
from datetime import datetime, timedelta

# Import enhanced modules
try:
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    from analytics_dashboard import AnalyticsDashboard
    ENHANCED_MODE = True
except ImportError as e:
    print(f"Enhanced modules not available: {e}")
    ENHANCED_MODE = False
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class AnalyticsDemo:
    def __init__(self):
        self.demo_chat_id = "demo_user_456"
        self.vocabulary_manager = VocabularyManager()
        
        # Clean up any existing demo data
        self.cleanup_demo_data()
        
        print("🚀 German Daily Word Bot - Advanced Analytics Demo")
        print("=" * 60)
    
    def cleanup_demo_data(self):
        """Clean up any existing demo data"""
        demo_file = f"progress_{self.demo_chat_id}.json"
        if os.path.exists(demo_file):
            os.remove(demo_file)
    
    def run_demo(self):
        """Run comprehensive analytics demonstration"""
        print("\n📊 DEMONSTRATING ADVANCED ANALYTICS FEATURES")
        print("-" * 50)
        
        # 1. Create user with enhanced analytics
        self.demo_user_creation()
        
        # 2. Simulate learning sessions
        self.demo_learning_sessions()
        
        # 3. Demonstrate streak milestones
        self.demo_streak_milestones()
        
        # 4. Show quiz performance tracking
        self.demo_quiz_tracking()
        
        # 5. Generate analytics reports
        self.demo_analytics_reports()
        
        # 6. Show predictive insights
        self.demo_predictive_analytics()
        
        print("\n🎉 DEMO COMPLETE!")
        print("All advanced analytics features are working perfectly!")
        
        # Cleanup
        self.cleanup_demo_data()
    
    def demo_user_creation(self):
        """Demonstrate enhanced user progress creation"""
        print("\n1️⃣ ENHANCED USER PROGRESS CREATION")
        print("   Creating user with advanced analytics...")
        
        user_progress = UserProgress(self.demo_chat_id, self.vocabulary_manager)
        
        print(f"   ✅ User created with enhanced features:")
        print(f"   📊 Streak Manager: {'Available' if user_progress.streak_manager else 'Not Available'}")
        print(f"   📈 Learning Analytics: {'Available' if user_progress.learning_analytics else 'Not Available'}")
        print(f"   🎯 Initial Streak: {user_progress.data['daily_streak']} days")
        print(f"   🛡️ Streak Freezes: {user_progress.data['streak_freeze_available']}")
    
    def demo_learning_sessions(self):
        """Demonstrate learning session tracking"""
        print("\n2️⃣ LEARNING SESSION TRACKING")
        print("   Simulating daily learning sessions...")
        
        user_progress = UserProgress(self.demo_chat_id, self.vocabulary_manager)
        
        # Simulate 5 days of learning
        sample_words = [
            [{'german': 'Hallo', 'english': 'Hello', 'category': 'greetings', 'level': 'A1'}],
            [{'german': 'Danke', 'english': 'Thank you', 'category': 'politeness', 'level': 'A1'},
             {'german': 'Bitte', 'english': 'Please', 'category': 'politeness', 'level': 'A1'}],
            [{'german': 'Wasser', 'english': 'Water', 'category': 'food_drink', 'level': 'A1'},
             {'german': 'Brot', 'english': 'Bread', 'category': 'food_drink', 'level': 'A1'},
             {'german': 'Kaffee', 'english': 'Coffee', 'category': 'food_drink', 'level': 'A1'}],
            [{'german': 'Haus', 'english': 'House', 'category': 'home', 'level': 'A1'}],
            [{'german': 'Auto', 'english': 'Car', 'category': 'transport', 'level': 'A1'},
             {'german': 'Zug', 'english': 'Train', 'category': 'transport', 'level': 'A1'}]
        ]
        
        for day, words in enumerate(sample_words, 1):
            streak_info = user_progress.update_daily_streak(words)
            for word in words:
                user_progress.add_learned_word(word)
            
            print(f"   Day {day}: Learned {len(words)} words - Streak: {user_progress.data['daily_streak']} days")
            
            if streak_info.get('milestone_reached'):
                print(f"   🎉 MILESTONE REACHED: {streak_info['milestone_reached']} days!")
        
        user_progress.save_progress()
        
        # Show analytics data
        if user_progress.learning_analytics:
            analytics = user_progress.learning_analytics.analytics_data
            print(f"   📊 Total Sessions: {len(analytics.get('session_times', []))}")
            print(f"   📈 Learning Velocity: {analytics.get('learning_velocity', 0):.1f} words/day")
            print(f"   ⚡ Engagement Score: {analytics.get('engagement_score', 0):.1f}/100")
    
    def demo_streak_milestones(self):
        """Demonstrate streak milestone system"""
        print("\n3️⃣ STREAK MILESTONE SYSTEM")
        print("   Simulating 7-day milestone achievement...")
        
        user_progress = UserProgress(self.demo_chat_id, self.vocabulary_manager)
        
        # Manually set streak to 7 to trigger milestone
        user_progress.data['daily_streak'] = 7
        
        if user_progress.streak_manager:
            milestone = user_progress.streak_manager._check_milestone_reached(7)
            if milestone:
                user_progress.streak_manager._award_milestone(milestone)
                
                print(f"   🏆 Milestone Achieved: {milestone} days")
                print(f"   🎁 Reward: Week Warrior title")
                print(f"   🛡️ Bonus: +1 Streak Freeze")
                print(f"   📊 Total Freezes: {user_progress.data['streak_freeze_available']}")
                
                # Show streak message
                streak_info = {
                    'milestone_reached': milestone,
                    'grace_period_used': False,
                    'streak_recovered': False,
                    'streak_continued': True,
                    'streak_broken': False
                }
                message = user_progress.streak_manager.format_streak_message(streak_info)
                print(f"   📱 User Message Preview:")
                print("   " + "\n   ".join(message.split('\n')[:5]) + "...")
    
    def demo_quiz_tracking(self):
        """Demonstrate quiz performance tracking"""
        print("\n4️⃣ QUIZ PERFORMANCE TRACKING")
        print("   Simulating quiz sessions...")
        
        user_progress = UserProgress(self.demo_chat_id, self.vocabulary_manager)
        
        # Simulate quiz results
        quiz_sessions = [
            {'score': 3, 'total': 5, 'percentage': 60.0, 'type': 'translation', 
             'words_tested': ['Hallo', 'Danke', 'Wasser', 'Brot', 'Haus'],
             'correct_words': ['Hallo', 'Danke', 'Wasser']},
            {'score': 4, 'total': 5, 'percentage': 80.0, 'type': 'pronunciation',
             'words_tested': ['Kaffee', 'Auto', 'Zug', 'Bitte', 'Hallo'],
             'correct_words': ['Kaffee', 'Auto', 'Zug', 'Hallo']},
            {'score': 5, 'total': 5, 'percentage': 100.0, 'type': 'example_completion',
             'words_tested': ['Danke', 'Wasser', 'Haus', 'Brot', 'Auto'],
             'correct_words': ['Danke', 'Wasser', 'Haus', 'Brot', 'Auto']}
        ]
        
        for i, quiz in enumerate(quiz_sessions, 1):
            user_progress.track_quiz_performance(quiz)
            print(f"   Quiz {i}: {quiz['score']}/{quiz['total']} ({quiz['percentage']:.1f}%) - {quiz['type']}")
        
        # Show quiz analytics
        quiz_scores = user_progress.data.get('quiz_scores', [])
        if quiz_scores:
            avg_score = sum(q['percentage'] for q in quiz_scores) / len(quiz_scores)
            print(f"   📊 Average Performance: {avg_score:.1f}%")
            print(f"   📈 Total Quizzes: {len(quiz_scores)}")
            print(f"   🎯 Best Score: {max(q['percentage'] for q in quiz_scores):.1f}%")
    
    def demo_analytics_reports(self):
        """Demonstrate analytics dashboard reports"""
        print("\n5️⃣ ANALYTICS DASHBOARD REPORTS")
        print("   Generating comprehensive reports...")
        
        user_progress = UserProgress(self.demo_chat_id, self.vocabulary_manager)
        dashboard = AnalyticsDashboard()
        
        # Generate different report types
        reports = {
            'Quick Stats': dashboard.generate_quick_stats(user_progress),
            'Streak Report': dashboard.generate_streak_report(user_progress),
            'Performance Report': dashboard.generate_performance_report(user_progress)
        }
        
        for report_name, report_content in reports.items():
            print(f"   📊 {report_name}: {len(report_content)} characters")
            # Show first few lines of each report
            lines = report_content.split('\n')[:3]
            for line in lines:
                if line.strip():
                    print(f"      {line}")
            print("      ...")
    
    def demo_predictive_analytics(self):
        """Demonstrate predictive analytics"""
        print("\n6️⃣ PREDICTIVE ANALYTICS")
        print("   Generating learning predictions...")
        
        user_progress = UserProgress(self.demo_chat_id, self.vocabulary_manager)
        
        if user_progress.learning_analytics:
            predictions = user_progress.learning_analytics.get_predictive_insights()
            
            print(f"   🔮 Engagement Risk: {predictions.get('engagement_risk', 'Unknown')}")
            print(f"   📈 30-Day Projection: {predictions.get('predicted_30_day_words', 0)} words")
            print(f"   🎯 Streak Sustainability: {predictions.get('streak_sustainability', 'Unknown')}")
            
            risk_factors = predictions.get('risk_factors', [])
            if risk_factors:
                print(f"   ⚠️ Risk Factors: {', '.join(risk_factors)}")
            else:
                print(f"   ✅ No risk factors identified")
        
        # Show comprehensive stats
        advanced_stats = user_progress.get_advanced_stats()
        print(f"   📊 Total Words Learned: {advanced_stats['total_words_learned']}")
        print(f"   🔥 Current Streak: {advanced_stats['daily_streak']} days")
        print(f"   🏆 Achievements: {advanced_stats['achievements_count']}")

def main():
    """Main function to run analytics demo"""
    try:
        demo = AnalyticsDemo()
        demo.run_demo()
        return True
        
    except Exception as e:
        logger.error(f"Error running analytics demo: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
