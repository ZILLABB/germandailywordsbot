#!/usr/bin/env python3
"""
Test Script for Advanced Analytics Features
Tests streak management, learning analytics, and dashboard functionality
"""

import os
import json
import logging
from datetime import datetime, timedelta

# Import enhanced modules
try:
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    from streak_manager import StreakManager
    from learning_analytics import LearningAnalytics
    from analytics_dashboard import AnalyticsDashboard
    ENHANCED_MODE = True
except ImportError as e:
    print(f"Enhanced modules not available: {e}")
    ENHANCED_MODE = False
    exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsTestSuite:
    def __init__(self):
        self.test_chat_id = "test_user_123"
        self.vocabulary_manager = VocabularyManager()
        self.test_results = []
        
        # Clean up any existing test data
        self.cleanup_test_data()
        
        logger.info("Analytics Test Suite initialized")
    
    def cleanup_test_data(self):
        """Clean up any existing test data"""
        test_file = f"progress_{self.test_chat_id}.json"
        if os.path.exists(test_file):
            os.remove(test_file)
            logger.info("Cleaned up existing test data")
    
    def run_all_tests(self):
        """Run all analytics tests"""
        logger.info("Starting comprehensive analytics tests...")
        
        # Test basic user progress creation
        self.test_user_progress_creation()
        
        # Test streak management
        self.test_streak_management()
        
        # Test learning analytics
        self.test_learning_analytics()
        
        # Test analytics dashboard
        self.test_analytics_dashboard()
        
        # Test milestone achievements
        self.test_milestone_achievements()
        
        # Test predictive analytics
        self.test_predictive_analytics()
        
        # Print results
        self.print_test_results()
        
        # Cleanup
        self.cleanup_test_data()
    
    def test_user_progress_creation(self):
        """Test enhanced user progress creation"""
        try:
            logger.info("Testing user progress creation...")
            
            user_progress = UserProgress(self.test_chat_id, self.vocabulary_manager)
            
            # Check if enhanced features are available
            has_streak_manager = user_progress.streak_manager is not None
            has_analytics = user_progress.learning_analytics is not None
            
            # Check data structure
            required_fields = [
                'longest_streak', 'total_study_days', 'streak_milestones',
                'streak_freeze_available', 'learning_analytics'
            ]
            
            all_fields_present = all(field in user_progress.data for field in required_fields)
            
            self.test_results.append({
                'test': 'User Progress Creation',
                'passed': has_streak_manager and has_analytics and all_fields_present,
                'details': f"Streak Manager: {has_streak_manager}, Analytics: {has_analytics}, Fields: {all_fields_present}"
            })
            
            logger.info("✅ User progress creation test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'User Progress Creation',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ User progress creation test failed: {e}")
    
    def test_streak_management(self):
        """Test advanced streak management features"""
        try:
            logger.info("Testing streak management...")
            
            user_progress = UserProgress(self.test_chat_id, self.vocabulary_manager)
            
            if not user_progress.streak_manager:
                self.test_results.append({
                    'test': 'Streak Management',
                    'passed': False,
                    'details': "Streak manager not available"
                })
                return
            
            # Test streak update
            streak_info = user_progress.streak_manager.update_streak()
            
            # Test streak stats
            stats = user_progress.streak_manager.get_streak_stats()
            
            # Test streak message formatting
            message = user_progress.streak_manager.format_streak_message(streak_info)
            
            # Verify expected fields
            expected_stats = ['current_streak', 'longest_streak', 'total_study_days', 
                            'streak_milestones_achieved', 'next_milestone']
            
            stats_complete = all(field in stats for field in expected_stats)
            
            self.test_results.append({
                'test': 'Streak Management',
                'passed': stats_complete and len(message) > 0,
                'details': f"Stats complete: {stats_complete}, Message length: {len(message)}"
            })
            
            logger.info("✅ Streak management test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Streak Management',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ Streak management test failed: {e}")
    
    def test_learning_analytics(self):
        """Test learning analytics functionality"""
        try:
            logger.info("Testing learning analytics...")
            
            user_progress = UserProgress(self.test_chat_id, self.vocabulary_manager)
            
            if not user_progress.learning_analytics:
                self.test_results.append({
                    'test': 'Learning Analytics',
                    'passed': False,
                    'details': "Learning analytics not available"
                })
                return
            
            # Simulate learning session
            test_words = [
                {'german': 'Hallo', 'english': 'Hello', 'category': 'greetings', 'level': 'A1'},
                {'german': 'Danke', 'english': 'Thank you', 'category': 'politeness', 'level': 'A1'},
                {'german': 'Wasser', 'english': 'Water', 'category': 'food_drink', 'level': 'A1'}
            ]
            
            user_progress.learning_analytics.track_learning_session(test_words, 10)
            
            # Test quiz performance tracking
            quiz_results = {
                'score': 2,
                'total': 3,
                'percentage': 66.7,
                'type': 'translation',
                'words_tested': ['Hallo', 'Danke', 'Wasser'],
                'correct_words': ['Hallo', 'Danke']
            }
            
            user_progress.learning_analytics.track_quiz_performance(quiz_results)
            
            # Get insights
            insights = user_progress.learning_analytics.get_learning_insights()
            
            # Get predictive insights
            predictive = user_progress.learning_analytics.get_predictive_insights()
            
            # Verify data structure
            has_insights = 'overall_performance' in insights
            has_predictive = 'engagement_risk' in predictive
            
            self.test_results.append({
                'test': 'Learning Analytics',
                'passed': has_insights and has_predictive,
                'details': f"Insights: {has_insights}, Predictive: {has_predictive}"
            })
            
            logger.info("✅ Learning analytics test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Learning Analytics',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ Learning analytics test failed: {e}")
    
    def test_analytics_dashboard(self):
        """Test analytics dashboard functionality"""
        try:
            logger.info("Testing analytics dashboard...")
            
            # Note: We can't actually send messages in test mode
            # So we'll test message generation only
            
            user_progress = UserProgress(self.test_chat_id, self.vocabulary_manager)
            
            # Add some test data
            user_progress.data['total_words_learned'] = 25
            user_progress.data['daily_streak'] = 5
            user_progress.save_progress()
            
            dashboard = AnalyticsDashboard()
            
            # Test different report types
            comprehensive = dashboard.generate_comprehensive_report(user_progress)
            streak_report = dashboard.generate_streak_report(user_progress)
            insights_report = dashboard.generate_insights_report(user_progress)
            performance = dashboard.generate_performance_report(user_progress)
            quick_stats = dashboard.generate_quick_stats(user_progress)
            
            # Verify all reports generated
            reports_generated = all(len(report) > 100 for report in [
                comprehensive, streak_report, insights_report, performance, quick_stats
            ])
            
            self.test_results.append({
                'test': 'Analytics Dashboard',
                'passed': reports_generated,
                'details': f"All reports generated: {reports_generated}"
            })
            
            logger.info("✅ Analytics dashboard test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Analytics Dashboard',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ Analytics dashboard test failed: {e}")
    
    def test_milestone_achievements(self):
        """Test milestone achievement system"""
        try:
            logger.info("Testing milestone achievements...")
            
            user_progress = UserProgress(self.test_chat_id, self.vocabulary_manager)
            
            if not user_progress.streak_manager:
                self.test_results.append({
                    'test': 'Milestone Achievements',
                    'passed': False,
                    'details': "Streak manager not available"
                })
                return
            
            # Simulate reaching a 7-day milestone
            user_progress.data['daily_streak'] = 7
            
            # Check milestone
            milestone = user_progress.streak_manager._check_milestone_reached(7)
            
            if milestone:
                user_progress.streak_manager._award_milestone(milestone)
            
            # Verify achievement was recorded
            achievements = user_progress.data.get('achievements', [])
            milestone_achieved = any(a.get('type') == 'streak_milestone' for a in achievements)
            
            # Check if streak freeze bonus was awarded
            freeze_bonus = user_progress.data.get('streak_freeze_available', 0) > 1
            
            self.test_results.append({
                'test': 'Milestone Achievements',
                'passed': milestone_achieved and freeze_bonus,
                'details': f"Achievement recorded: {milestone_achieved}, Bonus awarded: {freeze_bonus}"
            })
            
            logger.info("✅ Milestone achievements test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Milestone Achievements',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ Milestone achievements test failed: {e}")
    
    def test_predictive_analytics(self):
        """Test predictive analytics functionality"""
        try:
            logger.info("Testing predictive analytics...")
            
            user_progress = UserProgress(self.test_chat_id, self.vocabulary_manager)
            
            if not user_progress.learning_analytics:
                self.test_results.append({
                    'test': 'Predictive Analytics',
                    'passed': False,
                    'details': "Learning analytics not available"
                })
                return
            
            # Set up test data for prediction
            user_progress.data['daily_streak'] = 3
            user_progress.data['total_words_learned'] = 15
            
            # Set learning velocity
            user_progress.learning_analytics.analytics_data['learning_velocity'] = 2.5
            user_progress.learning_analytics.analytics_data['engagement_score'] = 65.0
            
            # Get predictive insights
            predictions = user_progress.learning_analytics.get_predictive_insights()
            
            # Verify prediction fields
            expected_fields = ['engagement_risk', 'predicted_30_day_words', 'streak_sustainability']
            predictions_complete = all(field in predictions for field in expected_fields)
            
            # Verify reasonable predictions
            reasonable_prediction = (
                predictions.get('predicted_30_day_words', 0) > 0 and
                predictions.get('engagement_risk') in ['Low', 'Medium', 'High'] and
                predictions.get('streak_sustainability') in ['Low', 'Medium', 'High']
            )
            
            self.test_results.append({
                'test': 'Predictive Analytics',
                'passed': predictions_complete and reasonable_prediction,
                'details': f"Complete: {predictions_complete}, Reasonable: {reasonable_prediction}"
            })
            
            logger.info("✅ Predictive analytics test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Predictive Analytics',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ Predictive analytics test failed: {e}")
    
    def print_test_results(self):
        """Print comprehensive test results"""
        logger.info("\n" + "="*60)
        logger.info("ANALYTICS TEST RESULTS")
        logger.info("="*60)
        
        passed_tests = 0
        total_tests = len(self.test_results)
        
        for result in self.test_results:
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            logger.info(f"{result['test']}: {status}")
            logger.info(f"   Details: {result['details']}")
            
            if result['passed']:
                passed_tests += 1
        
        logger.info("="*60)
        logger.info(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED! Analytics system is working correctly.")
        else:
            logger.warning(f"⚠️  {total_tests - passed_tests} tests failed. Check implementation.")
        
        logger.info("="*60)

def main():
    """Main function to run analytics tests"""
    try:
        test_suite = AnalyticsTestSuite()
        test_suite.run_all_tests()
        return True
        
    except Exception as e:
        logger.error(f"Error running analytics tests: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
