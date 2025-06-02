#!/usr/bin/env python3
"""
Weekly Analytics Report Sender for German Daily Word Bot
Sends comprehensive learning analytics to all active users
"""

import os
import json
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import enhanced modules
try:
    from analytics_dashboard import AnalyticsDashboard
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    ENHANCED_MODE = True
except ImportError:
    ENHANCED_MODE = False
    print("Enhanced modules not available. Weekly analytics requires enhanced mode.")
    exit(1)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weekly_analytics.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class WeeklyAnalyticsReporter:
    def __init__(self):
        self.dashboard = AnalyticsDashboard()
        self.vocabulary_manager = VocabularyManager()
        
        # Load active users
        self.active_users = self.load_active_users()
        
        logger.info("Weekly Analytics Reporter initialized")
    
    def load_active_users(self):
        """Load list of active users"""
        try:
            with open('active_users.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("No active users file found")
            return {}
    
    def should_send_weekly_report(self, chat_id: str) -> bool:
        """Check if weekly report should be sent to user"""
        try:
            user_progress = UserProgress(chat_id, self.vocabulary_manager)
            
            # Check if user has been active for at least a week
            start_date = datetime.fromisoformat(user_progress.data['start_date'])
            days_active = (datetime.now() - start_date).days
            
            if days_active < 7:
                return False
            
            # Check if user has learned at least 5 words
            total_words = user_progress.data.get('total_words_learned', 0)
            if total_words < 5:
                return False
            
            # Check if it's been a week since last report
            last_report = user_progress.data.get('last_weekly_report')
            if last_report:
                last_report_date = datetime.fromisoformat(last_report)
                days_since_report = (datetime.now() - last_report_date).days
                return days_since_report >= 7
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking weekly report status for {chat_id}: {e}")
            return False
    
    def generate_weekly_summary(self, chat_id: str) -> str:
        """Generate weekly learning summary"""
        try:
            user_progress = UserProgress(chat_id, self.vocabulary_manager)
            
            # Calculate weekly stats
            weekly_stats = self.calculate_weekly_stats(user_progress)
            
            message = "📊 **WEEKLY LEARNING SUMMARY** 📊\n"
            message += "=" * 40 + "\n\n"
            
            # This week's achievements
            message += "🎯 **THIS WEEK'S PROGRESS**\n"
            message += f"📚 Words Learned: {weekly_stats['words_this_week']}\n"
            message += f"🔥 Study Days: {weekly_stats['study_days_this_week']}/7\n"
            message += f"🎯 Daily Goal Achievement: {weekly_stats['goal_achievement']:.1f}%\n"
            message += f"⏱️ Total Study Time: {weekly_stats['total_study_time']} minutes\n\n"
            
            # Streak information
            if user_progress.streak_manager:
                streak_stats = user_progress.streak_manager.get_streak_stats()
                message += "🔥 **STREAK STATUS**\n"
                message += f"📈 Current Streak: {streak_stats['current_streak']} days\n"
                message += f"🏆 Longest Streak: {streak_stats['longest_streak']} days\n"
                message += f"📊 Consistency: {streak_stats['streak_percentage']:.1f}%\n\n"
            
            # Performance comparison
            message += "📈 **PERFORMANCE TRENDS**\n"
            if weekly_stats['improvement'] > 0:
                message += f"📊 Improvement: +{weekly_stats['improvement']:.1f}% vs last week\n"
                message += "🎉 You're getting better!\n\n"
            elif weekly_stats['improvement'] < 0:
                message += f"📊 Change: {weekly_stats['improvement']:.1f}% vs last week\n"
                message += "💪 Let's aim higher next week!\n\n"
            else:
                message += "📊 Steady progress maintained\n\n"
            
            # Category breakdown
            if weekly_stats['top_categories']:
                message += "🎯 **TOP LEARNING CATEGORIES**\n"
                for i, (category, count) in enumerate(weekly_stats['top_categories'][:3], 1):
                    message += f"{i}. {category.title()}: {count} words\n"
                message += "\n"
            
            # Recommendations for next week
            message += "💡 **NEXT WEEK'S FOCUS**\n"
            recommendations = self.generate_weekly_recommendations(user_progress, weekly_stats)
            for i, rec in enumerate(recommendations[:3], 1):
                message += f"{i}. {rec}\n"
            message += "\n"
            
            # Motivational message
            message += self.get_motivational_message(weekly_stats)
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating weekly summary for {chat_id}: {e}")
            return "📊 **WEEKLY SUMMARY**\n\nUnable to generate report at this time."
    
    def calculate_weekly_stats(self, user_progress: UserProgress) -> dict:
        """Calculate weekly learning statistics"""
        stats = {
            'words_this_week': 0,
            'study_days_this_week': 0,
            'goal_achievement': 0.0,
            'total_study_time': 0,
            'improvement': 0.0,
            'top_categories': []
        }
        
        try:
            # Get analytics data
            analytics_data = user_progress.data.get('learning_analytics', {})
            daily_counts = analytics_data.get('daily_word_counts', {})
            session_times = analytics_data.get('session_times', [])
            
            # Calculate this week's stats
            week_start = datetime.now() - timedelta(days=7)
            
            for i in range(7):
                date = (week_start + timedelta(days=i)).strftime('%Y-%m-%d')
                words_count = daily_counts.get(date, 0)
                stats['words_this_week'] += words_count
                if words_count > 0:
                    stats['study_days_this_week'] += 1
            
            # Calculate goal achievement
            weekly_goal = user_progress.data.get('preferences', {}).get('words_per_day', 3) * 7
            if weekly_goal > 0:
                stats['goal_achievement'] = (stats['words_this_week'] / weekly_goal) * 100
            
            # Calculate study time this week
            week_sessions = [s for s in session_times 
                           if datetime.fromisoformat(s['date']) >= week_start]
            stats['total_study_time'] = sum(s.get('duration_minutes', 5) for s in week_sessions)
            
            # Calculate improvement vs last week
            last_week_start = week_start - timedelta(days=7)
            last_week_words = 0
            for i in range(7):
                date = (last_week_start + timedelta(days=i)).strftime('%Y-%m-%d')
                last_week_words += daily_counts.get(date, 0)
            
            if last_week_words > 0:
                stats['improvement'] = ((stats['words_this_week'] - last_week_words) / last_week_words) * 100
            
            # Get top categories this week
            category_counts = {}
            for session in week_sessions:
                for category in session.get('categories', []):
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            stats['top_categories'] = sorted(category_counts.items(), 
                                           key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            logger.error(f"Error calculating weekly stats: {e}")
        
        return stats
    
    def generate_weekly_recommendations(self, user_progress: UserProgress, weekly_stats: dict) -> list:
        """Generate recommendations for next week"""
        recommendations = []
        
        # Study consistency recommendations
        if weekly_stats['study_days_this_week'] < 5:
            recommendations.append("Try to study at least 5 days next week for better consistency")
        
        # Goal achievement recommendations
        if weekly_stats['goal_achievement'] < 80:
            recommendations.append("Aim to reach your daily word goals more consistently")
        
        # Category diversity recommendations
        if len(weekly_stats['top_categories']) < 3:
            recommendations.append("Explore different vocabulary categories for well-rounded learning")
        
        # Streak recommendations
        if user_progress.streak_manager:
            streak_stats = user_progress.streak_manager.get_streak_stats()
            if streak_stats['current_streak'] < 7:
                recommendations.append("Focus on building a 7-day learning streak")
        
        # Performance-based recommendations
        if weekly_stats['improvement'] < 0:
            recommendations.append("Review previously learned words to strengthen retention")
        
        # Default recommendations if none generated
        if not recommendations:
            recommendations = [
                "Continue your excellent learning momentum",
                "Try challenging yourself with more advanced vocabulary",
                "Consider taking more quizzes to test your knowledge"
            ]
        
        return recommendations
    
    def get_motivational_message(self, weekly_stats: dict) -> str:
        """Get motivational message based on performance"""
        if weekly_stats['goal_achievement'] >= 100:
            return "🌟 Outstanding work! You exceeded your weekly goals!"
        elif weekly_stats['goal_achievement'] >= 80:
            return "🎉 Great job! You're making excellent progress!"
        elif weekly_stats['goal_achievement'] >= 60:
            return "👍 Good effort! Keep building that momentum!"
        elif weekly_stats['study_days_this_week'] >= 5:
            return "💪 Consistent effort pays off! Keep it up!"
        else:
            return "🚀 Every step counts! Let's make next week even better!"
    
    def send_weekly_reports_to_all(self) -> tuple:
        """Send weekly reports to all eligible users"""
        success_count = 0
        total_eligible = 0
        
        for chat_id, user_data in self.active_users.items():
            try:
                if self.should_send_weekly_report(chat_id):
                    total_eligible += 1
                    
                    # Generate and send comprehensive report
                    weekly_summary = self.generate_weekly_summary(chat_id)
                    
                    if self.dashboard.send_message(chat_id, weekly_summary):
                        success_count += 1
                        
                        # Update last report date
                        user_progress = UserProgress(chat_id, self.vocabulary_manager)
                        user_progress.data['last_weekly_report'] = datetime.now().isoformat()
                        user_progress.save_progress()
                        
                        logger.info(f"Weekly report sent to {chat_id}")
                    else:
                        logger.error(f"Failed to send weekly report to {chat_id}")
                
            except Exception as e:
                logger.error(f"Error processing weekly report for {chat_id}: {e}")
        
        return success_count, total_eligible
    
    def send_report_to_user(self, chat_id: str, report_type: str = "weekly") -> bool:
        """Send specific report to a single user"""
        try:
            if report_type == "weekly":
                message = self.generate_weekly_summary(chat_id)
            else:
                # Use dashboard for other report types
                return self.dashboard.send_analytics_report(chat_id, report_type)
            
            return self.dashboard.send_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"Error sending {report_type} report to {chat_id}: {e}")
            return False

def main():
    """Main function for weekly analytics reporter"""
    try:
        reporter = WeeklyAnalyticsReporter()
        
        # Send weekly reports to all eligible users
        success, total = reporter.send_weekly_reports_to_all()
        
        logger.info(f"Weekly analytics reports: {success}/{total} sent successfully")
        
        return success == total
        
    except Exception as e:
        logger.error(f"Error in weekly analytics reporter: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
