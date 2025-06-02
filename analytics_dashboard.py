#!/usr/bin/env python3
"""
Analytics Dashboard for German Daily Word Bot
Provides comprehensive learning analytics and insights for users
"""

import os
import json
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import enhanced modules
try:
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    from learning_analytics import LearningAnalytics
    ENHANCED_MODE = True
except ImportError:
    ENHANCED_MODE = False
    print("Enhanced modules not available. Analytics dashboard requires enhanced mode.")
    exit(1)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analytics_dashboard.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AnalyticsDashboard:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.vocabulary_manager = VocabularyManager()
        
        logger.info("Analytics Dashboard initialized")
    
    def send_analytics_report(self, chat_id: str, report_type: str = "comprehensive"):
        """Send analytics report to user"""
        try:
            user_progress = UserProgress(chat_id, self.vocabulary_manager)
            
            if report_type == "comprehensive":
                message = self.generate_comprehensive_report(user_progress)
            elif report_type == "streak":
                message = self.generate_streak_report(user_progress)
            elif report_type == "learning_insights":
                message = self.generate_insights_report(user_progress)
            elif report_type == "performance":
                message = self.generate_performance_report(user_progress)
            else:
                message = self.generate_quick_stats(user_progress)
            
            return self.send_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"Error generating analytics report for {chat_id}: {e}")
            return False
    
    def generate_comprehensive_report(self, user_progress: UserProgress) -> str:
        """Generate comprehensive analytics report"""
        stats = user_progress.get_advanced_stats()
        
        message = "📊 **COMPREHENSIVE LEARNING ANALYTICS** 📊\n"
        message += "=" * 50 + "\n\n"
        
        # Overview Section
        message += "🎯 **OVERVIEW**\n"
        message += f"📚 Total Words Learned: {stats['total_words_learned']}\n"
        message += f"🎓 Current Level: {stats['current_level']}\n"
        message += f"🔥 Current Streak: {stats.get('current_streak', 0)} days\n"
        message += f"🏆 Longest Streak: {stats.get('longest_streak', 0)} days\n"
        message += f"📈 Learning Velocity: {stats.get('learning_velocity', 0):.1f} words/day\n"
        message += f"⚡ Engagement Score: {stats.get('engagement_score', 0):.1f}/100\n\n"
        
        # Streak Analytics
        if stats.get('streak_milestones_achieved', 0) > 0:
            message += "🏅 **STREAK ACHIEVEMENTS**\n"
            message += f"🎖️ Milestones Achieved: {stats['streak_milestones_achieved']}\n"
            if stats.get('next_milestone'):
                message += f"🎯 Next Goal: {stats['next_milestone']} days "
                message += f"({stats.get('days_to_next_milestone', 0)} to go!)\n"
            message += f"🛡️ Streak Freezes Available: {stats.get('streak_freeze_available', 0)}\n"
            message += f"📊 Study Consistency: {stats.get('streak_percentage', 0):.1f}%\n\n"
        
        # Learning Progress by Level
        message += "📈 **PROGRESS BY LEVEL**\n"
        for level, count in stats['words_by_level'].items():
            if count > 0:
                message += f"{level}: {count} words\n"
        message += "\n"
        
        # Performance Insights
        if 'learning_insights' in stats:
            insights = stats['learning_insights']
            if 'overall_performance' in insights:
                perf = insights['overall_performance']
                message += "🎯 **PERFORMANCE ANALYSIS**\n"
                message += f"📊 Performance Level: {perf.get('performance_level', 'Unknown')}\n"
                message += f"🎯 Study Consistency: {perf.get('study_consistency', 0):.1f}%\n\n"
        
        # Recommendations
        if 'learning_insights' in stats and 'recommendations' in stats['learning_insights']:
            recommendations = stats['learning_insights']['recommendations']
            if recommendations:
                message += "💡 **PERSONALIZED RECOMMENDATIONS**\n"
                for i, rec in enumerate(recommendations[:3], 1):
                    message += f"{i}. {rec}\n"
                message += "\n"
        
        # Predictive Insights
        if 'predictive_insights' in stats:
            pred = stats['predictive_insights']
            message += "🔮 **PREDICTIVE INSIGHTS**\n"
            message += f"📈 30-Day Projection: {pred.get('predicted_30_day_words', 0)} words\n"
            message += f"⚠️ Engagement Risk: {pred.get('engagement_risk', 'Unknown')}\n"
            message += f"🎯 Streak Sustainability: {pred.get('streak_sustainability', 'Unknown')}\n\n"
        
        message += "🚀 Keep up the excellent work! Your dedication to learning German is paying off!"
        
        return message
    
    def generate_streak_report(self, user_progress: UserProgress) -> str:
        """Generate detailed streak analytics report"""
        if not user_progress.streak_manager:
            return "🔥 **STREAK REPORT**\n\nAdvanced streak tracking not available."
        
        stats = user_progress.streak_manager.get_streak_stats()
        
        message = "🔥 **DETAILED STREAK ANALYTICS** 🔥\n"
        message += "=" * 40 + "\n\n"
        
        message += f"📊 **Current Streak:** {stats['current_streak']} days\n"
        message += f"🏆 **Longest Streak:** {stats['longest_streak']} days\n"
        message += f"📚 **Total Study Days:** {stats['total_study_days']}\n"
        message += f"📈 **Consistency Rate:** {stats['streak_percentage']:.1f}%\n\n"
        
        message += "🏅 **ACHIEVEMENTS**\n"
        message += f"🎖️ Milestones Reached: {stats['streak_milestones_achieved']}\n"
        
        if stats['next_milestone']:
            message += f"🎯 Next Milestone: {stats['next_milestone']} days\n"
            message += f"📅 Days Remaining: {stats['days_to_next_milestone']}\n\n"
        
        message += "🛡️ **STREAK PROTECTION**\n"
        message += f"❄️ Freezes Available: {stats['streak_freeze_available']}\n"
        message += f"🔄 Freezes Used: {stats['streak_freeze_used']}\n"
        
        if stats['grace_period_active']:
            message += "⏰ Grace Period: ACTIVE\n"
        else:
            message += "⏰ Grace Period: Available\n"
        
        message += "\n💪 Stay consistent to build an even stronger streak!"
        
        return message
    
    def generate_insights_report(self, user_progress: UserProgress) -> str:
        """Generate learning insights and patterns report"""
        if not user_progress.learning_analytics:
            return "🧠 **LEARNING INSIGHTS**\n\nAdvanced analytics not available."
        
        insights = user_progress.learning_analytics.get_learning_insights()
        
        message = "🧠 **LEARNING INSIGHTS & PATTERNS** 🧠\n"
        message += "=" * 45 + "\n\n"
        
        # Learning Patterns
        if 'learning_patterns' in insights and 'message' not in insights['learning_patterns']:
            patterns = insights['learning_patterns']
            message += "⏰ **STUDY PATTERNS**\n"
            message += f"🕐 Preferred Study Time: {patterns.get('preferred_study_hour', 'Unknown')}:00\n"
            message += f"📅 Preferred Study Day: {patterns.get('preferred_study_day', 'Unknown')}\n"
            message += f"⏱️ Average Session: {patterns.get('average_session_length', 0):.1f} minutes\n"
            message += f"📊 Total Study Time: {patterns.get('total_study_time', 0):.0f} minutes\n\n"
        
        # Strengths and Weaknesses
        if 'strengths_weaknesses' in insights and 'message' not in insights['strengths_weaknesses']:
            sw = insights['strengths_weaknesses']
            
            message += "💪 **STRENGTHS & AREAS FOR IMPROVEMENT**\n"
            
            if 'strongest_categories' in sw:
                message += "🌟 Strongest Categories:\n"
                for cat, data in sw['strongest_categories'][:2]:
                    message += f"  • {cat.title()}: {data['words_learned']} words\n"
                message += "\n"
            
            if 'weakest_categories' in sw:
                message += "📈 Areas for Improvement:\n"
                for cat, data in sw['weakest_categories'][:2]:
                    message += f"  • {cat.title()}: {data['words_learned']} words\n"
                message += "\n"
        
        # Progress Trends
        if 'progress_trends' in insights and 'message' not in insights['progress_trends']:
            trends = insights['progress_trends']
            message += "📈 **PROGRESS TRENDS**\n"
            message += f"📊 Trend: {trends.get('trend', 'Unknown')}\n"
            message += f"📅 Recent Average: {trends.get('recent_average', 0):.1f} words/week\n"
            message += f"📆 Previous Average: {trends.get('previous_average', 0):.1f} words/week\n\n"
        
        # Retention Analysis
        if 'retention_analysis' in insights and 'message' not in insights['retention_analysis']:
            retention = insights['retention_analysis']
            message += "🧠 **MEMORY & RETENTION**\n"
            message += f"📊 Average Retention: {retention.get('average_retention', 0):.1f}%\n"
            message += f"🎯 High Retention Words: {retention.get('high_retention_words', 0)}\n"
            message += f"⚠️ Words Needing Review: {retention.get('low_retention_words', 0)}\n\n"
        
        # Recommendations
        if 'recommendations' in insights:
            message += "💡 **PERSONALIZED RECOMMENDATIONS**\n"
            for i, rec in enumerate(insights['recommendations'][:4], 1):
                message += f"{i}. {rec}\n"
        
        return message
    
    def generate_performance_report(self, user_progress: UserProgress) -> str:
        """Generate performance analysis report"""
        stats = user_progress.get_advanced_stats()
        
        message = "🎯 **PERFORMANCE ANALYSIS** 🎯\n"
        message += "=" * 35 + "\n\n"
        
        # Overall Performance
        if 'learning_insights' in stats and 'overall_performance' in stats['learning_insights']:
            perf = stats['learning_insights']['overall_performance']
            
            message += "📊 **OVERALL PERFORMANCE**\n"
            message += f"🎓 Performance Level: {perf.get('performance_level', 'Unknown')}\n"
            message += f"⚡ Engagement Score: {perf.get('engagement_score', 0):.1f}/100\n"
            message += f"🎯 Learning Velocity: {perf.get('learning_velocity', 0):.1f} words/day\n"
            message += f"📈 Study Consistency: {perf.get('study_consistency', 0):.1f}%\n\n"
        
        # Quiz Performance
        quiz_scores = user_progress.data.get('quiz_scores', [])
        if quiz_scores:
            recent_scores = quiz_scores[-5:]  # Last 5 quizzes
            avg_score = sum(q['percentage'] for q in recent_scores) / len(recent_scores)
            
            message += "🧠 **QUIZ PERFORMANCE**\n"
            message += f"📊 Recent Average: {avg_score:.1f}%\n"
            message += f"📈 Quizzes Taken: {len(quiz_scores)}\n"
            message += f"🎯 Best Score: {max(q['percentage'] for q in quiz_scores):.1f}%\n\n"
        
        # Level Progress
        message += "📚 **LEVEL PROGRESS**\n"
        current_level = stats['current_level']
        words_in_level = stats['words_by_level'].get(current_level, 0)
        
        level_targets = {'A1': 100, 'A2': 200, 'B1': 300, 'B2': 400}
        target = level_targets.get(current_level, 100)
        progress_pct = min((words_in_level / target) * 100, 100)
        
        message += f"🎓 Current Level: {current_level}\n"
        message += f"📊 Progress: {words_in_level}/{target} words ({progress_pct:.1f}%)\n"
        
        # Progress bar
        filled = int((progress_pct / 100) * 10)
        bar = "█" * filled + "░" * (10 - filled)
        message += f"📈 [{bar}] {progress_pct:.1f}%\n\n"
        
        # Achievements
        achievements = user_progress.data.get('achievements', [])
        if achievements:
            message += f"🏆 **ACHIEVEMENTS UNLOCKED:** {len(achievements)}\n"
            recent_achievements = achievements[-3:]  # Last 3 achievements
            for achievement in recent_achievements:
                if achievement['type'] == 'streak_milestone':
                    message += f"🔥 {achievement.get('title', 'Streak Milestone')}\n"
                elif achievement['type'] == 'level_up':
                    message += f"🎓 Level Up: {achievement.get('level', 'Unknown')}\n"
        
        return message
    
    def generate_quick_stats(self, user_progress: UserProgress) -> str:
        """Generate quick statistics overview"""
        stats = user_progress.get_stats()
        
        message = "📊 **QUICK STATS** 📊\n"
        message += "=" * 25 + "\n\n"
        
        message += f"📚 Words Learned: {stats['total_words_learned']}\n"
        message += f"🎓 Level: {stats['current_level']}\n"
        message += f"🔥 Streak: {stats['daily_streak']} days\n"
        message += f"🏆 Achievements: {stats['achievements_count']}\n"
        message += f"📝 Words Due for Review: {stats['words_due_for_review']}\n\n"
        
        message += "💪 Keep up the great work!"
        
        return message
    
    def send_message(self, chat_id: str, message: str) -> bool:
        """Send message to Telegram user"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Analytics report sent to {chat_id}")
                return True
            else:
                logger.error(f"Failed to send analytics report to {chat_id}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending analytics report to {chat_id}: {e}")
            return False

def main():
    """Main function for analytics dashboard"""
    try:
        dashboard = AnalyticsDashboard()
        
        # Example usage - you can modify this to send reports to specific users
        # dashboard.send_analytics_report("1224491488", "comprehensive")
        
        logger.info("Analytics dashboard ready")
        return True
        
    except Exception as e:
        logger.error(f"Error in analytics dashboard: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
