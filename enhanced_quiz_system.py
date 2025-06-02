#!/usr/bin/env python3
"""
Enhanced Quiz System for German Daily Word Bot
Integrates adaptive quizzes, difficulty analysis, and mastery-based progression
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Import our enhanced modules
try:
    from adaptive_quiz_system import AdaptiveQuizSystem
    from difficulty_analyzer import DifficultyAnalyzer
    from quiz_system import QuizSystem  # Original quiz system for fallback
    ENHANCED_QUIZ_AVAILABLE = True
except ImportError:
    ENHANCED_QUIZ_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedQuizSystem:
    def __init__(self, vocabulary_manager, user_progress):
        self.vocabulary_manager = vocabulary_manager
        self.user_progress = user_progress
        
        # Initialize enhanced components
        if ENHANCED_QUIZ_AVAILABLE:
            self.adaptive_quiz = AdaptiveQuizSystem(vocabulary_manager, user_progress)
            self.difficulty_analyzer = DifficultyAnalyzer(vocabulary_manager)
        else:
            self.adaptive_quiz = None
            self.difficulty_analyzer = None
        
        # Fallback to basic quiz system
        self.basic_quiz = QuizSystem(vocabulary_manager, user_progress)
        
        # Quiz scheduling and mastery tracking
        self.mastery_thresholds = {
            'introduced': 1,
            'familiar': 2,
            'practiced': 3,
            'mastered': 4,
            'expert': 5
        }
        
        # Quiz frequency based on performance
        self.quiz_frequency = {
            'struggling': 1,  # Daily quizzes
            'improving': 2,   # Every 2 days
            'proficient': 3,  # Every 3 days
            'advanced': 5     # Every 5 days
        }
    
    def should_send_enhanced_quiz(self) -> bool:
        """Determine if an enhanced quiz should be sent based on adaptive criteria"""
        stats = self.user_progress.get_stats()
        total_words = stats['total_words_learned']
        streak = stats['daily_streak']
        
        # Basic requirements
        if total_words < 5:
            return False
        
        # Get user performance level
        performance_level = self.get_user_performance_level()
        frequency = self.quiz_frequency.get(performance_level, 3)
        
        # Check if it's time for a quiz
        last_quiz_date = self.get_last_quiz_date()
        if last_quiz_date:
            days_since_quiz = (datetime.now() - last_quiz_date).days
            return days_since_quiz >= frequency
        
        # First quiz after learning enough words
        return total_words >= 10
    
    def get_user_performance_level(self) -> str:
        """Determine user's current performance level"""
        quiz_scores = self.user_progress.data.get('quiz_scores', [])
        
        if not quiz_scores:
            return 'improving'
        
        # Analyze recent performance
        recent_scores = quiz_scores[-5:]  # Last 5 quizzes
        avg_score = sum(q['percentage'] for q in recent_scores) / len(recent_scores)
        
        if avg_score < 60:
            return 'struggling'
        elif avg_score < 75:
            return 'improving'
        elif avg_score < 90:
            return 'proficient'
        else:
            return 'advanced'
    
    def get_last_quiz_date(self) -> Optional[datetime]:
        """Get the date of the last quiz"""
        quiz_scores = self.user_progress.data.get('quiz_scores', [])
        if not quiz_scores:
            return None
        
        last_quiz = quiz_scores[-1]
        return datetime.fromisoformat(last_quiz['date'])
    
    def generate_enhanced_quiz(self, quiz_type: str = 'adaptive', word_count: int = 5) -> Dict:
        """Generate an enhanced quiz with adaptive features"""
        if not ENHANCED_QUIZ_AVAILABLE or not self.adaptive_quiz:
            # Fallback to basic quiz
            return self.basic_quiz.generate_quiz(word_count=word_count)
        
        if quiz_type == 'adaptive':
            return self.adaptive_quiz.generate_adaptive_quiz(word_count)
        elif quiz_type == 'mastery_focused':
            return self.generate_mastery_focused_quiz(word_count)
        elif quiz_type == 'difficulty_progressive':
            return self.generate_difficulty_progressive_quiz(word_count)
        elif quiz_type == 'weak_areas':
            return self.generate_weak_areas_quiz(word_count)
        else:
            # Default to adaptive
            return self.adaptive_quiz.generate_adaptive_quiz(word_count)
    
    def generate_mastery_focused_quiz(self, word_count: int = 5) -> Dict:
        """Generate a quiz focused on words that need mastery improvement"""
        # Get words with low mastery levels
        low_mastery_words = []
        
        for level_data in self.user_progress.data['words_by_level'].values():
            for word_id in level_data['learned']:
                word_data = self.adaptive_quiz.get_word_by_id(word_id)
                if word_data:
                    mastery = self.adaptive_quiz.get_word_mastery_level(word_id)
                    if mastery < 4:  # Below 'mastered' level
                        word_data['current_mastery'] = mastery
                        low_mastery_words.append(word_data)
        
        # Sort by mastery level (lowest first)
        low_mastery_words.sort(key=lambda w: w['current_mastery'])
        
        # Select words for quiz
        quiz_words = low_mastery_words[:word_count]
        
        if not quiz_words:
            # Fallback to adaptive quiz
            return self.adaptive_quiz.generate_adaptive_quiz(word_count)
        
        quiz_data = {
            'type': 'mastery_focused',
            'questions': [],
            'created_at': datetime.now().isoformat(),
            'user_level': self.user_progress.get_current_level(),
            'focus': 'mastery_improvement'
        }
        
        # Generate questions with appropriate difficulty
        for word in quiz_words:
            mastery = word['current_mastery']
            
            # Choose question type based on mastery level
            if mastery <= 2:  # Introduced/Familiar
                question_types = ['translation_to_german', 'translation_to_english']
            elif mastery == 3:  # Practiced
                question_types = ['fill_in_blank', 'contextual_usage']
            else:  # Higher mastery
                question_types = ['sentence_construction', 'grammar_focus']
            
            quiz_type = random.choice(question_types)
            question = self.adaptive_quiz.create_adaptive_question(word, quiz_type)
            
            if question:
                question['mastery_focus'] = True
                question['target_mastery'] = mastery + 1
                quiz_data['questions'].append(question)
        
        return quiz_data
    
    def generate_difficulty_progressive_quiz(self, word_count: int = 5) -> Dict:
        """Generate a quiz with progressively increasing difficulty"""
        if not self.difficulty_analyzer:
            return self.adaptive_quiz.generate_adaptive_quiz(word_count)
        
        # Get learned words with difficulty analysis
        learned_words_with_difficulty = []
        
        for level_data in self.user_progress.data['words_by_level'].values():
            for word_id in level_data['learned']:
                word_data = self.adaptive_quiz.get_word_by_id(word_id)
                if word_data:
                    difficulty_analysis = self.difficulty_analyzer.analyze_word_difficulty(word_data)
                    word_data['difficulty_score'] = difficulty_analysis['overall_difficulty']
                    learned_words_with_difficulty.append(word_data)
        
        # Sort by difficulty
        learned_words_with_difficulty.sort(key=lambda w: w['difficulty_score'])
        
        # Select words with progressive difficulty
        quiz_words = []
        if len(learned_words_with_difficulty) >= word_count:
            step = len(learned_words_with_difficulty) // word_count
            for i in range(word_count):
                index = min(i * step, len(learned_words_with_difficulty) - 1)
                quiz_words.append(learned_words_with_difficulty[index])
        else:
            quiz_words = learned_words_with_difficulty[:word_count]
        
        quiz_data = {
            'type': 'difficulty_progressive',
            'questions': [],
            'created_at': datetime.now().isoformat(),
            'user_level': self.user_progress.get_current_level(),
            'focus': 'progressive_difficulty'
        }
        
        # Generate questions with increasing complexity
        question_types_by_difficulty = [
            ['translation_to_german', 'translation_to_english'],
            ['fill_in_blank', 'pronunciation_choice'],
            ['contextual_usage', 'audio_recognition'],
            ['sentence_construction', 'grammar_focus'],
            ['reverse_translation']
        ]
        
        for i, word in enumerate(quiz_words):
            # Choose question type based on position (difficulty progression)
            type_group_index = min(i, len(question_types_by_difficulty) - 1)
            available_types = question_types_by_difficulty[type_group_index]
            quiz_type = random.choice(available_types)
            
            question = self.adaptive_quiz.create_adaptive_question(word, quiz_type)
            
            if question:
                question['difficulty_progression'] = i + 1
                question['word_difficulty'] = word['difficulty_score']
                quiz_data['questions'].append(question)
        
        return quiz_data
    
    def generate_weak_areas_quiz(self, word_count: int = 5) -> Dict:
        """Generate a quiz focused on user's weak areas"""
        # Analyze user's weak categories and question types
        weak_areas = self.analyze_user_weak_areas()
        
        # Get words from weak categories
        weak_category_words = []
        
        if weak_areas['categories']:
            for category in weak_areas['categories'][:2]:  # Top 2 weak categories
                category_words = self.vocabulary_manager.words_by_category.get(category, [])
                for word in category_words:
                    if self.is_word_learned(word['german']):
                        weak_category_words.append(word)
        
        # Select words for quiz
        quiz_words = random.sample(weak_category_words, min(word_count, len(weak_category_words)))
        
        if not quiz_words:
            # Fallback if no weak areas identified
            return self.adaptive_quiz.generate_adaptive_quiz(word_count)
        
        quiz_data = {
            'type': 'weak_areas_focus',
            'questions': [],
            'created_at': datetime.now().isoformat(),
            'user_level': self.user_progress.get_current_level(),
            'focus': 'weak_areas_improvement',
            'target_areas': weak_areas
        }
        
        # Generate questions focusing on weak question types
        weak_question_types = weak_areas.get('question_types', ['translation_to_german'])
        
        for word in quiz_words:
            # Prefer weak question types
            if weak_question_types:
                quiz_type = random.choice(weak_question_types)
            else:
                quiz_type = 'translation_to_german'
            
            question = self.adaptive_quiz.create_adaptive_question(word, quiz_type)
            
            if question:
                question['weak_area_focus'] = True
                quiz_data['questions'].append(question)
        
        return quiz_data
    
    def analyze_user_weak_areas(self) -> Dict:
        """Analyze user's performance to identify weak areas"""
        weak_areas = {
            'categories': [],
            'question_types': [],
            'difficulty_levels': []
        }
        
        # Analyze quiz history if available
        if hasattr(self.user_progress, 'learning_analytics') and self.user_progress.learning_analytics:
            analytics = self.user_progress.learning_analytics.analytics_data
            
            # Analyze category performance
            category_performance = analytics.get('category_performance', {})
            if category_performance:
                # Find categories with low retention or few words learned
                weak_categories = []
                for category, data in category_performance.items():
                    words_learned = data.get('words_learned', 0)
                    avg_retention = data.get('average_retention', 100)
                    
                    if avg_retention < 70 or words_learned < 3:
                        weak_categories.append(category)
                
                weak_areas['categories'] = weak_categories[:3]  # Top 3 weak categories
        
        # Analyze recent quiz performance by question type
        quiz_scores = self.user_progress.data.get('quiz_scores', [])
        if quiz_scores:
            # This is simplified - in a full implementation, you'd track question type performance
            recent_performance = sum(q['percentage'] for q in quiz_scores[-5:]) / len(quiz_scores[-5:])
            
            if recent_performance < 70:
                weak_areas['question_types'] = ['fill_in_blank', 'contextual_usage']
            elif recent_performance < 85:
                weak_areas['question_types'] = ['sentence_construction', 'grammar_focus']
        
        return weak_areas
    
    def is_word_learned(self, word_id: str) -> bool:
        """Check if a word has been learned by the user"""
        for level_data in self.user_progress.data['words_by_level'].values():
            if word_id in level_data['learned']:
                return True
        return False
    
    def process_enhanced_quiz_results(self, quiz_data: Dict, user_answers: List) -> Dict:
        """Process quiz results with enhanced analytics and feedback"""
        if ENHANCED_QUIZ_AVAILABLE and self.adaptive_quiz:
            # Use adaptive processing
            results = self.adaptive_quiz.process_adaptive_quiz_results(quiz_data, user_answers)
        else:
            # Basic processing
            results = self.basic_quiz.process_quiz_results(quiz_data, user_answers)
        
        # Add enhanced feedback
        results['enhanced_feedback'] = self.generate_enhanced_feedback(quiz_data, results)
        results['next_steps'] = self.recommend_next_steps(results)
        results['mastery_progress'] = self.calculate_mastery_progress(quiz_data, results)
        
        # Update user analytics
        if hasattr(self.user_progress, 'track_quiz_performance'):
            enhanced_results = {
                'score': results['score'],
                'total': results['total'],
                'percentage': results['percentage'],
                'type': quiz_data.get('type', 'enhanced'),
                'words_tested': [q['word_id'] for q in quiz_data.get('questions', [])],
                'correct_words': [
                    quiz_data['questions'][i]['word_id'] 
                    for i, result in enumerate(results.get('detailed_results', []))
                    if result.get('correct', False)
                ]
            }
            self.user_progress.track_quiz_performance(enhanced_results)
        
        return results
    
    def generate_enhanced_feedback(self, quiz_data: Dict, results: Dict) -> str:
        """Generate detailed feedback based on quiz performance"""
        feedback = []
        
        score_percentage = results.get('percentage', 0)
        quiz_type = quiz_data.get('type', 'standard')
        
        # Performance-based feedback
        if score_percentage >= 90:
            feedback.append("🌟 Excellent work! Your German vocabulary knowledge is impressive!")
        elif score_percentage >= 80:
            feedback.append("👍 Great job! You're making solid progress in your German learning.")
        elif score_percentage >= 70:
            feedback.append("📈 Good effort! Keep practicing to strengthen your vocabulary.")
        else:
            feedback.append("💪 Don't worry! Every mistake is a learning opportunity. Keep going!")
        
        # Quiz type specific feedback
        if quiz_type == 'mastery_focused':
            feedback.append("🎯 This quiz focused on improving your mastery of specific words.")
        elif quiz_type == 'difficulty_progressive':
            feedback.append("📊 This quiz tested your ability with progressively challenging words.")
        elif quiz_type == 'weak_areas_focus':
            feedback.append("🔍 This quiz targeted your areas for improvement.")
        
        # Detailed results feedback
        if 'detailed_results' in results:
            correct_count = sum(1 for r in results['detailed_results'] if r.get('correct', False))
            total_count = len(results['detailed_results'])
            
            if correct_count == total_count:
                feedback.append("🎉 Perfect score! You've mastered these words!")
            elif correct_count >= total_count * 0.8:
                feedback.append("✨ Almost perfect! Just a few more practice sessions and you'll have it!")
        
        return " ".join(feedback)
    
    def recommend_next_steps(self, results: Dict) -> List[str]:
        """Recommend next learning steps based on quiz results"""
        recommendations = []
        
        score_percentage = results.get('percentage', 0)
        
        if score_percentage < 60:
            recommendations.extend([
                "Review the words you missed in today's lesson",
                "Practice with basic translation exercises",
                "Focus on one category at a time"
            ])
        elif score_percentage < 80:
            recommendations.extend([
                "Try using the missed words in sentences",
                "Practice with fill-in-the-blank exercises",
                "Review word pronunciation"
            ])
        else:
            recommendations.extend([
                "Challenge yourself with more complex question types",
                "Try constructing your own sentences",
                "Explore advanced vocabulary in your strong categories"
            ])
        
        # Add adaptive recommendations if available
        if 'recommendations' in results:
            recommendations.extend(results['recommendations'])
        
        return recommendations[:4]  # Limit to top 4 recommendations
    
    def calculate_mastery_progress(self, quiz_data: Dict, results: Dict) -> Dict:
        """Calculate mastery progress for words in the quiz"""
        mastery_progress = {
            'words_improved': 0,
            'words_mastered': 0,
            'overall_progress': 0.0
        }
        
        if 'detailed_results' in results:
            for result in results['detailed_results']:
                word_id = result.get('word_id')
                was_correct = result.get('correct', False)
                
                if word_id and ENHANCED_QUIZ_AVAILABLE and self.adaptive_quiz:
                    old_mastery = self.adaptive_quiz.get_word_mastery_level(word_id)
                    
                    # Simulate mastery improvement (in real implementation, this would be tracked)
                    if was_correct:
                        new_mastery = min(5, old_mastery + 0.5)
                        if new_mastery > old_mastery:
                            mastery_progress['words_improved'] += 1
                        if new_mastery >= 4:  # Mastered level
                            mastery_progress['words_mastered'] += 1
        
        # Calculate overall progress
        total_words = len(results.get('detailed_results', []))
        if total_words > 0:
            mastery_progress['overall_progress'] = (mastery_progress['words_improved'] / total_words) * 100
        
        return mastery_progress
    
    def format_enhanced_quiz_message(self, quiz_data: Dict) -> str:
        """Format enhanced quiz as Telegram message"""
        if not quiz_data or not quiz_data.get('questions'):
            return "No quiz available at this time."
        
        quiz_type = quiz_data.get('type', 'standard')
        difficulty_level = quiz_data.get('difficulty_level', 'Mixed')
        
        # Header with quiz type information
        message = "🧠 **Enhanced German Quiz** 🧠\n"
        message += f"📊 Type: {quiz_type.replace('_', ' ').title()}\n"
        message += f"🎯 Level: {quiz_data.get('user_level', 'A1')}\n"
        message += f"⚡ Difficulty: {difficulty_level}\n"
        message += f"❓ Questions: {len(quiz_data['questions'])}\n"
        message += "=" * 40 + "\n\n"
        
        # Format questions
        for i, question in enumerate(quiz_data['questions'], 1):
            message += f"**Question {i}:**\n"
            message += f"{question['question']}\n\n"
            
            if question['type'] == 'fill_in_blank':
                message += "💭 Type your answer:\n"
                if 'hint' in question:
                    message += f"💡 Hint: {question['hint']}\n"
            else:
                # Multiple choice
                for j, option in enumerate(question.get('options', [])):
                    letter = chr(65 + j)  # A, B, C, D
                    message += f"{letter}) {option}\n"
            
            message += f"\n💡 *Answer: "
            if question['type'] == 'fill_in_blank':
                message += f"{question['correct_answer']}*\n"
            else:
                correct_index = question.get('correct_answer', 0)
                message += f"{chr(65 + correct_index)}*\n"
            
            message += f"📝 {question.get('explanation', '')}\n"
            
            if 'hint' in question and question['type'] != 'fill_in_blank':
                message += f"💡 {question['hint']}\n"
            
            message += "\n" + "-" * 30 + "\n\n"
        
        # Footer with encouragement
        message += "🎯 **How did you do?**\n"
        message += "📚 Review any words you missed and keep practicing!\n"
        message += "🚀 Your German vocabulary is growing stronger every day!"
        
        return message
