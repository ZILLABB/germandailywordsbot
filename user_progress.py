#!/usr/bin/env python3
"""
User Progress Tracking System for German Daily Word Bot
Manages CEFR level progression, learned words, and spaced repetition
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Import new analytics modules
try:
    from streak_manager import StreakManager
    from learning_analytics import LearningAnalytics
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    logger.warning("Advanced analytics modules not available")

class UserProgress:
    def __init__(self, chat_id: str, vocabulary_manager=None):
        self.chat_id = chat_id
        self.progress_file = f"progress_{chat_id}.json"
        self.data = self.load_progress()

        # Initialize advanced analytics if available
        if ANALYTICS_AVAILABLE:
            self.streak_manager = StreakManager(self)
            if vocabulary_manager:
                self.learning_analytics = LearningAnalytics(self, vocabulary_manager)
            else:
                self.learning_analytics = None
        else:
            self.streak_manager = None
            self.learning_analytics = None
    
    def load_progress(self) -> Dict:
        """Load user progress from file or create new profile"""
        default_progress = {
            "chat_id": self.chat_id,
            "current_level": "A1",
            "start_date": datetime.now().isoformat(),
            "total_words_learned": 0,
            "words_by_level": {
                "A1": {"learned": [], "review_due": []},
                "A2": {"learned": [], "review_due": []},
                "B1": {"learned": [], "review_due": []},
                "B2": {"learned": [], "review_due": []}
            },
            "daily_streak": 0,
            "longest_streak": 0,
            "total_study_days": 0,
            "streak_milestones": [],
            "last_lesson_date": None,
            "streak_freeze_used": 0,
            "streak_freeze_available": 1,
            "grace_period_active": False,
            "grace_period_expires": None,
            "quiz_scores": [],
            "weekly_goals": {
                "words_per_week": 21,  # 3 words × 7 days
                "current_week_count": 0,
                "week_start": datetime.now().isoformat()
            },
            "learning_analytics": {
                "session_times": [],
                "daily_word_counts": {},
                "category_performance": {},
                "difficulty_progression": [],
                "retention_rates": {},
                "learning_velocity": 0.0,
                "engagement_score": 0.0
            },
            "preferences": {
                "words_per_day": 3,
                "include_grammar": True,
                "include_cultural_notes": True,
                "difficulty_progression": "automatic"
            },
            "achievements": [],
            "spaced_repetition": {}
        }
        
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Merge with default to ensure all fields exist
                for key, value in default_progress.items():
                    if key not in data:
                        data[key] = value
                return data
            else:
                return default_progress
        except Exception as e:
            logger.error(f"Error loading progress for {self.chat_id}: {e}")
            return default_progress
    
    def save_progress(self):
        """Save user progress to file"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"Progress saved for user {self.chat_id}")
        except Exception as e:
            logger.error(f"Error saving progress for {self.chat_id}: {e}")
    
    def add_learned_word(self, word_data: Dict):
        """Add a word to learned vocabulary with spaced repetition schedule"""
        word_id = word_data['german']
        level = word_data['level']
        
        # Add to learned words if not already there
        if word_id not in self.data['words_by_level'][level]['learned']:
            self.data['words_by_level'][level]['learned'].append(word_id)
            self.data['total_words_learned'] += 1
            
            # Schedule for spaced repetition
            self.schedule_spaced_repetition(word_id, word_data)
            
            logger.info(f"Added word '{word_id}' to learned vocabulary for user {self.chat_id}")
    
    def schedule_spaced_repetition(self, word_id: str, word_data: Dict):
        """Schedule word for spaced repetition using increasing intervals"""
        now = datetime.now()
        
        # Spaced repetition intervals: 1 day, 3 days, 1 week, 2 weeks, 1 month
        intervals = [1, 3, 7, 14, 30]
        
        self.data['spaced_repetition'][word_id] = {
            'word_data': word_data,
            'review_count': 0,
            'next_review': (now + timedelta(days=intervals[0])).isoformat(),
            'intervals': intervals,
            'last_reviewed': now.isoformat(),
            'success_rate': 0.0
        }
    
    def get_words_for_review(self) -> List[Dict]:
        """Get words that are due for review today"""
        now = datetime.now()
        due_words = []
        
        for word_id, review_data in self.data['spaced_repetition'].items():
            next_review = datetime.fromisoformat(review_data['next_review'])
            if next_review <= now:
                due_words.append(review_data['word_data'])
        
        return due_words
    
    def update_review_result(self, word_id: str, success: bool):
        """Update spaced repetition schedule based on review result"""
        if word_id not in self.data['spaced_repetition']:
            return
        
        review_data = self.data['spaced_repetition'][word_id]
        review_data['review_count'] += 1
        review_data['last_reviewed'] = datetime.now().isoformat()
        
        # Update success rate
        old_rate = review_data['success_rate']
        count = review_data['review_count']
        review_data['success_rate'] = (old_rate * (count - 1) + (1.0 if success else 0.0)) / count
        
        # Calculate next review interval
        intervals = review_data['intervals']
        current_interval_index = min(review_data['review_count'] - 1, len(intervals) - 1)
        
        if success:
            # Move to next interval if successful
            next_interval_index = min(current_interval_index + 1, len(intervals) - 1)
        else:
            # Reset to first interval if failed
            next_interval_index = 0
        
        next_interval = intervals[next_interval_index]
        next_review = datetime.now() + timedelta(days=next_interval)
        review_data['next_review'] = next_review.isoformat()
    
    def should_level_up(self) -> bool:
        """Check if user should progress to next CEFR level"""
        current_level = self.data['current_level']
        level_words = self.data['words_by_level'][current_level]['learned']
        
        # Level progression criteria
        level_requirements = {
            'A1': 50,   # 50 words to move to A2
            'A2': 100,  # 100 additional words to move to B1
            'B1': 150,  # 150 additional words to move to B2
            'B2': 200   # B2 is the target level
        }
        
        if current_level in level_requirements:
            required_words = level_requirements[current_level]
            return len(level_words) >= required_words
        
        return False
    
    def level_up(self) -> Optional[str]:
        """Progress user to next CEFR level"""
        level_progression = {'A1': 'A2', 'A2': 'B1', 'B1': 'B2'}
        current_level = self.data['current_level']
        
        if current_level in level_progression:
            new_level = level_progression[current_level]
            self.data['current_level'] = new_level
            
            # Add achievement
            achievement = {
                'type': 'level_up',
                'level': new_level,
                'date': datetime.now().isoformat(),
                'words_learned': self.data['total_words_learned']
            }
            self.data['achievements'].append(achievement)
            
            logger.info(f"User {self.chat_id} leveled up to {new_level}")
            return new_level
        
        return None
    
    def update_daily_streak(self, words_learned: List[Dict] = None):
        """Update daily learning streak with advanced tracking"""
        if self.streak_manager:
            # Use advanced streak manager
            streak_info = self.streak_manager.update_streak()

            # Track learning session if analytics available
            if self.learning_analytics and words_learned:
                self.learning_analytics.track_learning_session(words_learned)
                self.learning_analytics.save_analytics()

            return streak_info
        else:
            # Fallback to basic streak tracking
            today = datetime.now().date().isoformat()
            last_lesson = self.data.get('last_lesson_date')

            if last_lesson:
                last_date = datetime.fromisoformat(last_lesson).date()
                today_date = datetime.now().date()

                if last_date == today_date:
                    # Already learned today
                    return {'streak_continued': False, 'streak_broken': False}
                elif last_date == today_date - timedelta(days=1):
                    # Consecutive day
                    self.data['daily_streak'] += 1
                    streak_info = {'streak_continued': True, 'streak_broken': False}
                else:
                    # Streak broken
                    self.data['daily_streak'] = 1
                    streak_info = {'streak_continued': False, 'streak_broken': True}
            else:
                # First lesson
                self.data['daily_streak'] = 1
                streak_info = {'streak_continued': True, 'streak_broken': False}

            self.data['last_lesson_date'] = today

            # Check for streak achievements
            streak = self.data['daily_streak']
            if streak in [7, 30, 100, 365]:
                achievement = {
                    'type': 'streak',
                    'days': streak,
                    'date': datetime.now().isoformat()
                }
                self.data['achievements'].append(achievement)
                streak_info['milestone_reached'] = streak

            return streak_info
    
    def get_current_level(self) -> str:
        """Get user's current CEFR level"""
        return self.data['current_level']
    
    def get_stats(self) -> Dict:
        """Get user learning statistics"""
        return {
            'current_level': self.data['current_level'],
            'total_words_learned': self.data['total_words_learned'],
            'daily_streak': self.data['daily_streak'],
            'words_by_level': {
                level: len(data['learned']) 
                for level, data in self.data['words_by_level'].items()
            },
            'achievements_count': len(self.data['achievements']),
            'words_due_for_review': len(self.get_words_for_review())
        }
    
    def get_preferences(self) -> Dict:
        """Get user preferences"""
        return self.data['preferences']
    
    def update_preferences(self, preferences: Dict):
        """Update user preferences"""
        self.data['preferences'].update(preferences)
        self.save_progress()

    def get_advanced_stats(self) -> Dict:
        """Get comprehensive learning statistics with analytics"""
        basic_stats = self.get_stats()

        if self.streak_manager:
            streak_stats = self.streak_manager.get_streak_stats()
            basic_stats.update(streak_stats)

        if self.learning_analytics:
            insights = self.learning_analytics.get_learning_insights()
            basic_stats['learning_insights'] = insights

            predictive = self.learning_analytics.get_predictive_insights()
            basic_stats['predictive_insights'] = predictive

        return basic_stats

    def get_streak_message(self, streak_info: Dict) -> str:
        """Get formatted streak message"""
        if self.streak_manager:
            return self.streak_manager.format_streak_message(streak_info)
        else:
            # Basic streak message
            if streak_info.get('milestone_reached'):
                return f"🎉 Milestone reached: {streak_info['milestone_reached']} day streak!"
            elif streak_info.get('streak_continued'):
                return f"🔥 Streak continues: {self.data['daily_streak']} days!"
            elif streak_info.get('streak_broken'):
                return "💔 Streak broken, but starting fresh!"
            else:
                return "📚 Keep learning!"

    def track_quiz_performance(self, quiz_results: Dict):
        """Track quiz performance for analytics"""
        if self.learning_analytics:
            self.learning_analytics.track_quiz_performance(quiz_results)
            self.learning_analytics.save_analytics()

        # Also add to basic quiz scores
        self.data['quiz_scores'].append({
            'date': datetime.now().isoformat(),
            'score': quiz_results.get('score', 0),
            'total': quiz_results.get('total', 0),
            'percentage': quiz_results.get('percentage', 0)
        })
        self.save_progress()
