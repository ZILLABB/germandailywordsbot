#!/usr/bin/env python3
"""
Progress Statistics and Analytics for German Daily Word Bot
Provides detailed learning analytics and progress visualization
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from user_progress import UserProgress
from vocabulary_manager import VocabularyManager

logger = logging.getLogger(__name__)

class ProgressAnalytics:
    def __init__(self, chat_id: str):
        self.chat_id = chat_id
        self.user_progress = UserProgress(chat_id)
        self.vocabulary_manager = VocabularyManager()
    
    def generate_weekly_report(self) -> str:
        """Generate a comprehensive weekly progress report"""
        stats = self.user_progress.get_stats()
        
        # Calculate weekly progress
        week_start = datetime.now() - timedelta(days=7)
        weekly_words = self.get_words_learned_since(week_start)
        
        report = "📊 **Weekly German Learning Report**\n"
        report += "=" * 40 + "\n\n"
        
        # Overall Progress
        report += f"🎯 **Current Level:** {stats['current_level']}\n"
        report += f"📚 **Total Vocabulary:** {stats['total_words_learned']} words\n"
        report += f"🔥 **Learning Streak:** {stats['daily_streak']} days\n"
        report += f"📈 **This Week:** +{len(weekly_words)} new words\n\n"
        
        # Level Breakdown
        report += "📋 **Progress by Level:**\n"
        for level, count in stats['words_by_level'].items():
            percentage = self.get_level_completion_percentage(level)
            progress_bar = self.create_progress_bar(percentage)
            report += f"{level}: {count} words {progress_bar} {percentage:.1f}%\n"
        
        report += "\n"
        
        # Category Analysis
        category_stats = self.get_category_distribution()
        report += "🏷️ **Vocabulary by Category:**\n"
        for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"• {category.replace('_', ' ').title()}: {count} words\n"
        
        report += "\n"
        
        # Spaced Repetition Status
        review_stats = self.get_review_statistics()
        report += "🔄 **Review Status:**\n"
        report += f"• Due today: {review_stats['due_today']} words\n"
        report += f"• Due this week: {review_stats['due_week']} words\n"
        report += f"• Average success rate: {review_stats['avg_success_rate']:.1f}%\n\n"
        
        # Achievements
        recent_achievements = self.get_recent_achievements()
        if recent_achievements:
            report += "🏆 **Recent Achievements:**\n"
            for achievement in recent_achievements:
                report += f"• {self.format_achievement(achievement)}\n"
            report += "\n"
        
        # Recommendations
        recommendations = self.generate_recommendations()
        report += "💡 **Recommendations:**\n"
        for rec in recommendations:
            report += f"• {rec}\n"
        
        report += "\n📈 Keep up the excellent work! 🇩🇪"
        
        return report
    
    def get_words_learned_since(self, since_date: datetime) -> List[str]:
        """Get words learned since a specific date"""
        # This is a simplified version - in a real implementation,
        # you'd track learning dates for each word
        weekly_words = []
        for level_data in self.user_progress.data['words_by_level'].values():
            weekly_words.extend(level_data['learned'])
        
        # For now, return recent words (this would be improved with actual timestamps)
        return weekly_words[-7:] if len(weekly_words) >= 7 else weekly_words
    
    def get_level_completion_percentage(self, level: str) -> float:
        """Calculate completion percentage for a CEFR level"""
        level_targets = {
            'A1': 100,  # Target words for each level
            'A2': 200,
            'B1': 300,
            'B2': 400
        }
        
        learned_count = len(self.user_progress.data['words_by_level'][level]['learned'])
        target = level_targets.get(level, 100)
        
        return min((learned_count / target) * 100, 100.0)
    
    def create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """Create a visual progress bar"""
        filled = int((percentage / 100) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"
    
    def get_category_distribution(self) -> Dict[str, int]:
        """Get distribution of learned words by category"""
        category_counts = {}
        
        for level_data in self.user_progress.data['words_by_level'].values():
            for word_id in level_data['learned']:
                word_data = self.get_word_by_id(word_id)
                if word_data:
                    category = word_data.get('category', 'unknown')
                    category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts
    
    def get_review_statistics(self) -> Dict:
        """Get spaced repetition review statistics"""
        now = datetime.now()
        due_today = 0
        due_week = 0
        success_rates = []
        
        for word_id, review_data in self.user_progress.data.get('spaced_repetition', {}).items():
            next_review = datetime.fromisoformat(review_data['next_review'])
            
            if next_review.date() == now.date():
                due_today += 1
            elif next_review <= now + timedelta(days=7):
                due_week += 1
            
            success_rates.append(review_data.get('success_rate', 0.0))
        
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0
        
        return {
            'due_today': due_today,
            'due_week': due_week,
            'avg_success_rate': avg_success_rate * 100
        }
    
    def get_recent_achievements(self, days: int = 7) -> List[Dict]:
        """Get achievements from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_achievements = []
        
        for achievement in self.user_progress.data.get('achievements', []):
            achievement_date = datetime.fromisoformat(achievement['date'])
            if achievement_date >= cutoff_date:
                recent_achievements.append(achievement)
        
        return recent_achievements
    
    def format_achievement(self, achievement: Dict) -> str:
        """Format achievement for display"""
        if achievement['type'] == 'level_up':
            return f"🎓 Reached level {achievement['level']}!"
        elif achievement['type'] == 'streak':
            return f"🔥 {achievement['days']}-day learning streak!"
        elif achievement['type'] == 'vocabulary_milestone':
            return f"📚 Learned {achievement['word_count']} words!"
        else:
            return f"🏆 {achievement['type'].replace('_', ' ').title()}"
    
    def generate_recommendations(self) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []
        stats = self.user_progress.get_stats()
        
        # Review recommendations
        if stats['words_due_for_review'] > 5:
            recommendations.append("📝 You have several words due for review. Consider doing a quiz session!")
        
        # Level progression
        current_level = stats['current_level']
        if self.user_progress.should_level_up():
            recommendations.append(f"🎯 You're ready to progress from {current_level}! Keep learning consistently.")
        
        # Category diversity
        category_stats = self.get_category_distribution()
        if len(category_stats) < 5:
            recommendations.append("🌈 Try learning words from different categories to build well-rounded vocabulary.")
        
        # Streak maintenance
        if stats['daily_streak'] < 7:
            recommendations.append("🔥 Build a daily learning habit! Consistency is key to language learning.")
        elif stats['daily_streak'] >= 30:
            recommendations.append("🏆 Amazing streak! Consider increasing your daily word count.")
        
        # Grammar focus
        recommendations.append("📚 Don't forget to practice German grammar alongside vocabulary!")
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def get_word_by_id(self, word_id: str) -> Optional[Dict]:
        """Get word data by German word ID"""
        for word in self.vocabulary_manager.words:
            if word['german'] == word_id:
                return word
        return None
    
    def export_progress_data(self) -> Dict:
        """Export all progress data for backup or analysis"""
        return {
            'user_data': self.user_progress.data,
            'statistics': self.user_progress.get_stats(),
            'export_date': datetime.now().isoformat(),
            'vocabulary_version': len(self.vocabulary_manager.words)
        }
    
    def generate_learning_insights(self) -> str:
        """Generate AI-like learning insights"""
        stats = self.user_progress.get_stats()
        category_stats = self.get_category_distribution()
        
        insights = "🧠 **Learning Insights**\n"
        insights += "=" * 30 + "\n\n"
        
        # Learning pace analysis
        total_words = stats['total_words_learned']
        streak = stats['daily_streak']
        
        if streak > 0:
            words_per_day = total_words / max(streak, 1)
            insights += f"📊 **Learning Pace:** {words_per_day:.1f} words per day\n"
            
            if words_per_day >= 3:
                insights += "✅ Excellent pace! You're building vocabulary efficiently.\n"
            elif words_per_day >= 2:
                insights += "👍 Good steady progress. Consider slight increase if possible.\n"
            else:
                insights += "💪 Room for improvement. Try to be more consistent.\n"
        
        insights += "\n"
        
        # Vocabulary balance
        if category_stats:
            most_learned = max(category_stats.items(), key=lambda x: x[1])
            least_learned = min(category_stats.items(), key=lambda x: x[1])
            
            insights += f"🎯 **Strongest Area:** {most_learned[0].replace('_', ' ').title()} ({most_learned[1]} words)\n"
            insights += f"📈 **Growth Area:** {least_learned[0].replace('_', ' ').title()} ({least_learned[1]} words)\n\n"
        
        # Level progression insight
        current_level = stats['current_level']
        level_progress = self.get_level_completion_percentage(current_level)
        
        insights += f"🎓 **Level Progress:** {level_progress:.1f}% through {current_level}\n"
        
        if level_progress >= 80:
            insights += "🚀 Almost ready for the next level!\n"
        elif level_progress >= 50:
            insights += "📚 Halfway there! Keep up the momentum.\n"
        else:
            insights += "🌱 Building a strong foundation in this level.\n"
        
        return insights

def main():
    """Generate and display progress report"""
    import sys
    
    if len(sys.argv) > 1:
        chat_id = sys.argv[1]
    else:
        chat_id = os.getenv('CHAT_ID', 'default_user')
    
    analytics = ProgressAnalytics(chat_id)
    
    print("📊 Generating Weekly Progress Report...")
    print("=" * 50)
    
    weekly_report = analytics.generate_weekly_report()
    print(weekly_report)
    
    print("\n" + "=" * 50)
    
    insights = analytics.generate_learning_insights()
    print(insights)

if __name__ == "__main__":
    main()
