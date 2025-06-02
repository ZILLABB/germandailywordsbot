#!/usr/bin/env python3
"""
Comprehensive Learning Analytics System for German Daily Word Bot
Provides detailed insights, performance tracking, and predictive analytics
"""

import json
import os
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class LearningAnalytics:
    def __init__(self, user_progress, vocabulary_manager):
        self.user_progress = user_progress
        self.vocabulary_manager = vocabulary_manager
        self.analytics_data = self.user_progress.data.get('learning_analytics', {})
    
    def track_learning_session(self, words_learned: List[Dict], session_duration: int = None):
        """Track a learning session with detailed metrics"""
        session_data = {
            'date': datetime.now().isoformat(),
            'words_count': len(words_learned),
            'words': [word['german'] for word in words_learned],
            'categories': [word.get('category', 'unknown') for word in words_learned],
            'levels': [word.get('level', 'A1') for word in words_learned],
            'duration_minutes': session_duration or 5  # Default 5 minutes
        }
        
        # Add to session history
        if 'session_times' not in self.analytics_data:
            self.analytics_data['session_times'] = []
        
        self.analytics_data['session_times'].append(session_data)
        
        # Update daily word counts
        today = datetime.now().strftime('%Y-%m-%d')
        if 'daily_word_counts' not in self.analytics_data:
            self.analytics_data['daily_word_counts'] = {}
        
        self.analytics_data['daily_word_counts'][today] = (
            self.analytics_data['daily_word_counts'].get(today, 0) + len(words_learned)
        )
        
        # Update category performance
        self._update_category_performance(words_learned)
        
        # Calculate learning velocity
        self._calculate_learning_velocity()
        
        # Update engagement score
        self._update_engagement_score()
        
        logger.info(f"Learning session tracked for user {self.user_progress.chat_id}: "
                   f"{len(words_learned)} words, {session_duration} minutes")
    
    def track_quiz_performance(self, quiz_results: Dict):
        """Track quiz performance for analytics"""
        quiz_data = {
            'date': datetime.now().isoformat(),
            'score': quiz_results.get('score', 0),
            'total': quiz_results.get('total', 0),
            'percentage': quiz_results.get('percentage', 0),
            'quiz_type': quiz_results.get('type', 'unknown'),
            'words_tested': quiz_results.get('words_tested', [])
        }
        
        # Add to quiz history
        if 'quiz_performance' not in self.analytics_data:
            self.analytics_data['quiz_performance'] = []
        
        self.analytics_data['quiz_performance'].append(quiz_data)
        
        # Update retention rates
        self._update_retention_rates(quiz_results)
        
        logger.info(f"Quiz performance tracked: {quiz_results.get('percentage', 0):.1f}%")
    
    def _update_category_performance(self, words_learned: List[Dict]):
        """Update performance tracking by category"""
        if 'category_performance' not in self.analytics_data:
            self.analytics_data['category_performance'] = {}
        
        for word in words_learned:
            category = word.get('category', 'unknown')
            if category not in self.analytics_data['category_performance']:
                self.analytics_data['category_performance'][category] = {
                    'words_learned': 0,
                    'total_sessions': 0,
                    'average_retention': 0.0,
                    'difficulty_score': 0.0
                }
            
            self.analytics_data['category_performance'][category]['words_learned'] += 1
            self.analytics_data['category_performance'][category]['total_sessions'] += 1
    
    def _calculate_learning_velocity(self):
        """Calculate learning velocity (words per day over time)"""
        if not self.analytics_data.get('daily_word_counts'):
            self.analytics_data['learning_velocity'] = 0.0
            return
        
        # Get last 30 days of data
        recent_counts = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            count = self.analytics_data['daily_word_counts'].get(date, 0)
            recent_counts.append(count)
        
        # Calculate average
        if recent_counts:
            self.analytics_data['learning_velocity'] = statistics.mean(recent_counts)
        else:
            self.analytics_data['learning_velocity'] = 0.0
    
    def _update_engagement_score(self):
        """Calculate user engagement score based on multiple factors"""
        score = 0.0
        
        # Streak contribution (40%)
        streak = self.user_progress.data.get('daily_streak', 0)
        streak_score = min(40, streak * 2)  # Max 40 points
        score += streak_score
        
        # Learning velocity contribution (30%)
        velocity = self.analytics_data.get('learning_velocity', 0)
        velocity_score = min(30, velocity * 10)  # Max 30 points
        score += velocity_score
        
        # Quiz performance contribution (20%)
        quiz_score = self._get_average_quiz_performance() * 0.2
        score += quiz_score
        
        # Consistency contribution (10%)
        consistency = self._calculate_consistency_score() * 0.1
        score += consistency
        
        self.analytics_data['engagement_score'] = min(100.0, score)
    
    def _get_average_quiz_performance(self) -> float:
        """Get average quiz performance percentage"""
        quiz_data = self.analytics_data.get('quiz_performance', [])
        if not quiz_data:
            return 0.0
        
        recent_quizzes = quiz_data[-10:]  # Last 10 quizzes
        percentages = [q['percentage'] for q in recent_quizzes]
        return statistics.mean(percentages) if percentages else 0.0
    
    def _calculate_consistency_score(self) -> float:
        """Calculate learning consistency score"""
        daily_counts = self.analytics_data.get('daily_word_counts', {})
        if len(daily_counts) < 7:
            return 0.0
        
        # Get last 30 days
        recent_days = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            count = daily_counts.get(date, 0)
            recent_days.append(1 if count > 0 else 0)
        
        return (sum(recent_days) / len(recent_days)) * 100
    
    def _update_retention_rates(self, quiz_results: Dict):
        """Update word retention rates based on quiz performance"""
        if 'retention_rates' not in self.analytics_data:
            self.analytics_data['retention_rates'] = {}
        
        words_tested = quiz_results.get('words_tested', [])
        correct_answers = quiz_results.get('correct_words', [])
        
        for word in words_tested:
            if word not in self.analytics_data['retention_rates']:
                self.analytics_data['retention_rates'][word] = {
                    'tests_taken': 0,
                    'correct_answers': 0,
                    'retention_rate': 0.0
                }
            
            self.analytics_data['retention_rates'][word]['tests_taken'] += 1
            if word in correct_answers:
                self.analytics_data['retention_rates'][word]['correct_answers'] += 1
            
            # Update retention rate
            tests = self.analytics_data['retention_rates'][word]['tests_taken']
            correct = self.analytics_data['retention_rates'][word]['correct_answers']
            self.analytics_data['retention_rates'][word]['retention_rate'] = (correct / tests) * 100
    
    def get_learning_insights(self) -> Dict:
        """Generate comprehensive learning insights"""
        insights = {
            'overall_performance': self._analyze_overall_performance(),
            'learning_patterns': self._analyze_learning_patterns(),
            'strengths_weaknesses': self._analyze_strengths_weaknesses(),
            'recommendations': self._generate_recommendations(),
            'progress_trends': self._analyze_progress_trends(),
            'retention_analysis': self._analyze_retention()
        }
        
        return insights
    
    def _analyze_overall_performance(self) -> Dict:
        """Analyze overall learning performance"""
        total_words = self.user_progress.data.get('total_words_learned', 0)
        streak = self.user_progress.data.get('daily_streak', 0)
        engagement = self.analytics_data.get('engagement_score', 0)
        velocity = self.analytics_data.get('learning_velocity', 0)
        
        # Performance level classification
        if engagement >= 80:
            performance_level = "Excellent"
        elif engagement >= 60:
            performance_level = "Good"
        elif engagement >= 40:
            performance_level = "Fair"
        else:
            performance_level = "Needs Improvement"
        
        return {
            'total_words_learned': total_words,
            'current_streak': streak,
            'engagement_score': engagement,
            'learning_velocity': velocity,
            'performance_level': performance_level,
            'study_consistency': self._calculate_consistency_score()
        }
    
    def _analyze_learning_patterns(self) -> Dict:
        """Analyze learning patterns and habits"""
        sessions = self.analytics_data.get('session_times', [])
        if not sessions:
            return {'message': 'Not enough data for pattern analysis'}
        
        # Analyze session timing
        session_hours = []
        session_days = []
        
        for session in sessions[-30:]:  # Last 30 sessions
            dt = datetime.fromisoformat(session['date'])
            session_hours.append(dt.hour)
            session_days.append(dt.weekday())
        
        # Find most common study time
        if session_hours:
            most_common_hour = max(set(session_hours), key=session_hours.count)
            most_common_day = max(set(session_days), key=session_days.count)
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            return {
                'preferred_study_hour': most_common_hour,
                'preferred_study_day': day_names[most_common_day],
                'average_session_length': statistics.mean([s.get('duration_minutes', 5) for s in sessions]),
                'total_study_time': sum([s.get('duration_minutes', 5) for s in sessions])
            }
        
        return {'message': 'Insufficient session data'}
    
    def _analyze_strengths_weaknesses(self) -> Dict:
        """Analyze learning strengths and weaknesses by category"""
        category_perf = self.analytics_data.get('category_performance', {})
        retention_rates = self.analytics_data.get('retention_rates', {})
        
        if not category_perf:
            return {'message': 'Not enough category data'}
        
        # Calculate category scores
        category_scores = {}
        for category, data in category_perf.items():
            # Get retention rate for words in this category
            category_words = [word for word, rate_data in retention_rates.items() 
                            if self._get_word_category(word) == category]
            
            if category_words:
                avg_retention = statistics.mean([
                    retention_rates[word]['retention_rate'] for word in category_words
                ])
            else:
                avg_retention = 0.0
            
            category_scores[category] = {
                'words_learned': data['words_learned'],
                'retention_rate': avg_retention,
                'overall_score': (data['words_learned'] * 0.3) + (avg_retention * 0.7)
            }
        
        # Find strengths and weaknesses
        if category_scores:
            sorted_categories = sorted(category_scores.items(), 
                                     key=lambda x: x[1]['overall_score'], reverse=True)
            
            return {
                'strongest_categories': sorted_categories[:3],
                'weakest_categories': sorted_categories[-3:],
                'category_breakdown': category_scores
            }
        
        return {'message': 'Insufficient category data'}
    
    def _get_word_category(self, word: str) -> str:
        """Get category for a specific word"""
        for vocab_word in self.vocabulary_manager.words:
            if vocab_word['german'] == word:
                return vocab_word.get('category', 'unknown')
        return 'unknown'
    
    def _generate_recommendations(self) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        # Analyze engagement score
        engagement = self.analytics_data.get('engagement_score', 0)
        if engagement < 50:
            recommendations.append("Try to maintain a daily learning routine to improve engagement")
        
        # Analyze streak
        streak = self.user_progress.data.get('daily_streak', 0)
        if streak < 7:
            recommendations.append("Focus on building a consistent daily streak")
        
        # Analyze learning velocity
        velocity = self.analytics_data.get('learning_velocity', 0)
        if velocity < 2:
            recommendations.append("Consider increasing your daily word target")
        
        # Analyze quiz performance
        avg_quiz = self._get_average_quiz_performance()
        if avg_quiz < 70:
            recommendations.append("Spend more time reviewing previously learned words")
        
        # Category-specific recommendations
        strengths_weaknesses = self._analyze_strengths_weaknesses()
        if 'weakest_categories' in strengths_weaknesses:
            weak_cats = strengths_weaknesses['weakest_categories']
            if weak_cats:
                weakest = weak_cats[0][0]
                recommendations.append(f"Focus on improving {weakest} vocabulary")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _analyze_progress_trends(self) -> Dict:
        """Analyze learning progress trends over time"""
        daily_counts = self.analytics_data.get('daily_word_counts', {})
        
        if len(daily_counts) < 7:
            return {'message': 'Need at least 7 days of data for trend analysis'}
        
        # Get last 30 days
        dates = []
        counts = []
        
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            dates.append(date)
            counts.append(daily_counts.get(date, 0))
        
        # Calculate trend
        if len(counts) >= 2:
            recent_avg = statistics.mean(counts[:7])  # Last week
            older_avg = statistics.mean(counts[7:14])  # Week before
            
            if recent_avg > older_avg:
                trend = "Improving"
            elif recent_avg < older_avg:
                trend = "Declining"
            else:
                trend = "Stable"
            
            return {
                'trend': trend,
                'recent_average': recent_avg,
                'previous_average': older_avg,
                'total_words_this_month': sum(counts)
            }
        
        return {'message': 'Insufficient data for trend analysis'}
    
    def _analyze_retention(self) -> Dict:
        """Analyze word retention patterns"""
        retention_data = self.analytics_data.get('retention_rates', {})
        
        if not retention_data:
            return {'message': 'No retention data available'}
        
        retention_rates = [data['retention_rate'] for data in retention_data.values()]
        
        if retention_rates:
            return {
                'average_retention': statistics.mean(retention_rates),
                'best_retention': max(retention_rates),
                'worst_retention': min(retention_rates),
                'words_tested': len(retention_rates),
                'high_retention_words': len([r for r in retention_rates if r >= 80]),
                'low_retention_words': len([r for r in retention_rates if r < 50])
            }
        
        return {'message': 'No retention data available'}
    
    def save_analytics(self):
        """Save analytics data back to user progress"""
        self.user_progress.data['learning_analytics'] = self.analytics_data
        self.user_progress.save_progress()
    
    def get_predictive_insights(self) -> Dict:
        """Generate predictive insights for user engagement"""
        engagement = self.analytics_data.get('engagement_score', 0)
        streak = self.user_progress.data.get('daily_streak', 0)
        velocity = self.analytics_data.get('learning_velocity', 0)
        
        # Risk assessment
        risk_factors = []
        if engagement < 40:
            risk_factors.append("Low engagement score")
        if streak < 3:
            risk_factors.append("Short learning streak")
        if velocity < 1:
            risk_factors.append("Low learning velocity")
        
        # Predict likelihood of continued engagement
        if len(risk_factors) >= 2:
            engagement_risk = "High"
        elif len(risk_factors) == 1:
            engagement_risk = "Medium"
        else:
            engagement_risk = "Low"
        
        return {
            'engagement_risk': engagement_risk,
            'risk_factors': risk_factors,
            'predicted_30_day_words': int(velocity * 30),
            'streak_sustainability': "High" if streak >= 14 else "Medium" if streak >= 7 else "Low"
        }
