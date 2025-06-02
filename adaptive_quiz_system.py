#!/usr/bin/env python3
"""
Advanced Adaptive Quiz System for German Daily Word Bot
Implements intelligent question types, difficulty adjustment, and mastery-based progression
"""

import json
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class AdaptiveQuizSystem:
    def __init__(self, vocabulary_manager, user_progress):
        self.vocabulary_manager = vocabulary_manager
        self.user_progress = user_progress
        
        # Enhanced quiz types with difficulty levels
        self.quiz_types = {
            'translation_to_german': {'difficulty': 1, 'mastery_weight': 1.0},
            'translation_to_english': {'difficulty': 1, 'mastery_weight': 1.0},
            'fill_in_blank': {'difficulty': 2, 'mastery_weight': 1.5},
            'sentence_construction': {'difficulty': 3, 'mastery_weight': 2.0},
            'contextual_usage': {'difficulty': 2, 'mastery_weight': 1.5},
            'grammar_focus': {'difficulty': 3, 'mastery_weight': 2.0},
            'audio_recognition': {'difficulty': 2, 'mastery_weight': 1.5},
            'reverse_translation': {'difficulty': 4, 'mastery_weight': 2.5},
            'pronunciation_choice': {'difficulty': 2, 'mastery_weight': 1.0},
            'cultural_context': {'difficulty': 2, 'mastery_weight': 1.5}
        }
        
        # Mastery levels
        self.mastery_levels = {
            0: 'Unknown',
            1: 'Introduced', 
            2: 'Familiar',
            3: 'Practiced',
            4: 'Mastered',
            5: 'Expert'
        }
        
        # Difficulty thresholds for adaptive selection
        self.difficulty_thresholds = {
            'beginner': 1,
            'intermediate': 2,
            'advanced': 3,
            'expert': 4
        }
    
    def get_user_difficulty_level(self) -> str:
        """Determine user's current difficulty level based on performance"""
        stats = self.user_progress.get_stats()
        total_words = stats['total_words_learned']
        
        # Get recent quiz performance
        quiz_scores = self.user_progress.data.get('quiz_scores', [])
        if quiz_scores:
            recent_scores = quiz_scores[-10:]  # Last 10 quizzes
            avg_performance = sum(q['percentage'] for q in recent_scores) / len(recent_scores)
        else:
            avg_performance = 0
        
        # Determine difficulty level
        if total_words < 20 or avg_performance < 60:
            return 'beginner'
        elif total_words < 50 or avg_performance < 75:
            return 'intermediate'
        elif total_words < 100 or avg_performance < 85:
            return 'advanced'
        else:
            return 'expert'
    
    def get_adaptive_quiz_types(self) -> List[str]:
        """Get appropriate quiz types based on user's difficulty level"""
        user_level = self.get_user_difficulty_level()
        max_difficulty = self.difficulty_thresholds[user_level]
        
        # Filter quiz types by difficulty
        suitable_types = [
            quiz_type for quiz_type, info in self.quiz_types.items()
            if info['difficulty'] <= max_difficulty
        ]
        
        return suitable_types
    
    def get_word_mastery_level(self, word_id: str) -> int:
        """Get mastery level for a specific word"""
        if not hasattr(self.user_progress, 'learning_analytics') or not self.user_progress.learning_analytics:
            return 1  # Default to 'Introduced'
        
        retention_data = self.user_progress.learning_analytics.analytics_data.get('retention_rates', {})
        
        if word_id not in retention_data:
            return 1
        
        word_retention = retention_data[word_id]
        tests_taken = word_retention.get('tests_taken', 0)
        retention_rate = word_retention.get('retention_rate', 0)
        
        # Calculate mastery based on tests taken and retention rate
        if tests_taken == 0:
            return 1
        elif tests_taken < 3:
            return 2 if retention_rate >= 50 else 1
        elif retention_rate >= 90 and tests_taken >= 5:
            return 5  # Expert
        elif retention_rate >= 80:
            return 4  # Mastered
        elif retention_rate >= 70:
            return 3  # Practiced
        elif retention_rate >= 50:
            return 2  # Familiar
        else:
            return 1  # Introduced
    
    def select_words_for_quiz(self, word_count: int = 5) -> List[Dict]:
        """Intelligently select words for quiz based on mastery and spaced repetition"""
        # Get all learned words
        all_learned = []
        for level_data in self.user_progress.data['words_by_level'].values():
            for word_id in level_data['learned']:
                word_data = self.get_word_by_id(word_id)
                if word_data:
                    all_learned.append(word_data)
        
        if not all_learned:
            return []
        
        # Score words based on priority (lower score = higher priority)
        word_scores = []
        for word in all_learned:
            word_id = word['german']
            mastery = self.get_word_mastery_level(word_id)
            
            # Priority factors
            mastery_score = 6 - mastery  # Lower mastery = higher priority
            
            # Check if due for review
            review_due = self.is_word_due_for_review(word_id)
            review_score = 0 if review_due else 2
            
            # Recent performance
            recent_errors = self.get_recent_error_count(word_id)
            error_score = recent_errors * 0.5
            
            total_score = mastery_score + review_score + error_score + random.uniform(0, 1)
            word_scores.append((word, total_score))
        
        # Sort by score and select top words
        word_scores.sort(key=lambda x: x[1])
        selected_words = [word for word, score in word_scores[:word_count]]
        
        return selected_words
    
    def generate_adaptive_quiz(self, word_count: int = 5, focus_area: str = None) -> Dict:
        """Generate an adaptive quiz with intelligent question selection"""
        # Select appropriate quiz types
        available_types = self.get_adaptive_quiz_types()
        
        # Select words intelligently
        quiz_words = self.select_words_for_quiz(word_count)
        
        if not quiz_words:
            return None
        
        quiz_data = {
            'type': 'adaptive_mixed',
            'questions': [],
            'created_at': datetime.now().isoformat(),
            'user_level': self.user_progress.get_current_level(),
            'difficulty_level': self.get_user_difficulty_level(),
            'adaptive_features': True
        }
        
        # Generate questions with varied types
        for word in quiz_words:
            # Choose question type based on word mastery and available types
            mastery = self.get_word_mastery_level(word['german'])
            
            # Higher mastery words get more challenging question types
            if mastery >= 4:  # Mastered/Expert
                preferred_types = [t for t in available_types if self.quiz_types[t]['difficulty'] >= 2]
            elif mastery >= 3:  # Practiced
                preferred_types = [t for t in available_types if self.quiz_types[t]['difficulty'] >= 1]
            else:  # Introduced/Familiar
                preferred_types = [t for t in available_types if self.quiz_types[t]['difficulty'] <= 2]
            
            if not preferred_types:
                preferred_types = available_types
            
            quiz_type = random.choice(preferred_types)
            question = self.create_adaptive_question(word, quiz_type)
            
            if question:
                question['mastery_level'] = mastery
                question['difficulty'] = self.quiz_types[quiz_type]['difficulty']
                quiz_data['questions'].append(question)
        
        return quiz_data
    
    def create_adaptive_question(self, word: Dict, quiz_type: str) -> Optional[Dict]:
        """Create an adaptive question of specified type"""
        if quiz_type == 'fill_in_blank':
            return self.create_fill_in_blank_question(word)
        elif quiz_type == 'sentence_construction':
            return self.create_sentence_construction_question(word)
        elif quiz_type == 'contextual_usage':
            return self.create_contextual_usage_question(word)
        elif quiz_type == 'grammar_focus':
            return self.create_grammar_focus_question(word)
        elif quiz_type == 'audio_recognition':
            return self.create_audio_recognition_question(word)
        elif quiz_type == 'reverse_translation':
            return self.create_reverse_translation_question(word)
        else:
            # Fall back to basic quiz system for standard types
            from quiz_system import QuizSystem
            basic_quiz = QuizSystem(self.vocabulary_manager, self.user_progress)
            return basic_quiz.create_question(word, quiz_type)
    
    def create_fill_in_blank_question(self, word: Dict) -> Dict:
        """Create a fill-in-the-blank question"""
        example = word.get('example', '')
        target_word = word['german']
        
        if target_word not in example:
            # Create a simple sentence if no example available
            example = f"Ich möchte {target_word} haben."
        
        # Create blanked sentence
        blank_sentence = example.replace(target_word, "____")
        
        return {
            'word_id': word['german'],
            'question': f"Fill in the blank:\n{blank_sentence}",
            'correct_answer': target_word,
            'type': 'fill_in_blank',
            'explanation': f"Complete sentence: {example}",
            'translation': word.get('example_translation', ''),
            'hint': f"English: {word['english']}"
        }
    
    def create_sentence_construction_question(self, word: Dict) -> Dict:
        """Create a sentence construction question"""
        target_word = word['german']
        
        # Create word components for sentence building
        sentence_parts = [
            target_word,
            "ist",
            "sehr",
            "gut"
        ]
        
        # Add some distractors
        distractors = ["nicht", "aber", "oder", "und"]
        all_parts = sentence_parts + random.sample(distractors, 2)
        random.shuffle(all_parts)
        
        correct_sentence = f"{target_word} ist sehr gut."
        
        return {
            'word_id': word['german'],
            'question': f"Construct a sentence using '{target_word}' from these words:",
            'word_parts': all_parts,
            'correct_answer': correct_sentence,
            'type': 'sentence_construction',
            'explanation': f"Correct sentence: {correct_sentence}",
            'hint': f"Use '{target_word}' as the subject"
        }
    
    def create_contextual_usage_question(self, word: Dict) -> Dict:
        """Create a contextual usage question"""
        target_word = word['german']
        category = word.get('category', 'general')
        
        # Create context-appropriate scenarios
        contexts = {
            'food_drink': f"At a restaurant, you want to order {word['english']}. What do you say?",
            'greetings': f"You meet someone in the morning. How do you greet them?",
            'transport': f"You need to travel using {word['english']}. What do you look for?",
            'home': f"You're describing your house. How do you mention the {word['english']}?",
            'general': f"In conversation, when would you use '{target_word}'?"
        }
        
        context = contexts.get(category, contexts['general'])
        
        # Generate options
        correct_answer = f"Ich möchte {target_word}, bitte." if category == 'food_drink' else target_word
        distractors = self.get_contextual_distractors(word, category)
        
        options = [correct_answer] + distractors[:3]
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        return {
            'word_id': word['german'],
            'question': context,
            'options': options,
            'correct_answer': correct_index,
            'type': 'contextual_usage',
            'explanation': f"'{target_word}' means '{word['english']}' and is used in this context.",
            'category': category
        }
    
    def create_grammar_focus_question(self, word: Dict) -> Dict:
        """Create a grammar-focused question"""
        target_word = word['german']
        word_type = word.get('word_type', 'noun')
        
        if word_type == 'noun':
            # Focus on articles
            question = f"What is the correct article for '{target_word}'?"
            # This is simplified - in a real implementation, you'd have gender data
            options = ["der", "die", "das", "ein"]
            correct_answer = 0  # Simplified
        elif word_type == 'verb':
            # Focus on conjugation
            question = f"How do you conjugate '{target_word}' for 'ich'?"
            options = [f"ich {target_word}e", f"ich {target_word}", f"ich {target_word}t", f"ich {target_word}st"]
            correct_answer = 0  # Simplified
        else:
            # General usage
            question = f"Which sentence correctly uses '{target_word}'?"
            correct_sentence = word.get('example', f"{target_word} ist gut.")
            options = [correct_sentence, f"{target_word} sind gut.", f"Der {target_word} gut.", f"Gut {target_word} ist."]
            correct_answer = 0
        
        return {
            'word_id': word['german'],
            'question': question,
            'options': options,
            'correct_answer': correct_answer,
            'type': 'grammar_focus',
            'explanation': f"Grammar rule for {word_type}: {target_word}",
            'word_type': word_type
        }
    
    def create_audio_recognition_question(self, word: Dict) -> Dict:
        """Create an audio recognition question (simulated)"""
        target_word = word['german']
        pronunciation = word.get('pronunciation', f"/{target_word}/")
        
        # Simulate audio with pronunciation guide
        question = f"🔊 Listen to the pronunciation: {pronunciation}\nWhich word is being pronounced?"
        
        # Generate similar-sounding distractors
        distractors = self.get_phonetic_distractors(word)
        options = [target_word] + distractors[:3]
        random.shuffle(options)
        correct_index = options.index(target_word)
        
        return {
            'word_id': word['german'],
            'question': question,
            'options': options,
            'correct_answer': correct_index,
            'type': 'audio_recognition',
            'explanation': f"The pronunciation {pronunciation} corresponds to '{target_word}' ({word['english']})",
            'pronunciation': pronunciation
        }
    
    def create_reverse_translation_question(self, word: Dict) -> Dict:
        """Create a reverse translation question with context"""
        target_word = word['german']
        english_word = word['english']
        
        # Create a more complex translation scenario
        context_sentence = f"In the context of daily conversation, how would you express '{english_word}' in German when talking about {word.get('category', 'general topics')}?"
        
        # Generate contextually appropriate distractors
        distractors = self.get_semantic_distractors(word)
        options = [target_word] + distractors[:3]
        random.shuffle(options)
        correct_index = options.index(target_word)
        
        return {
            'word_id': word['german'],
            'question': context_sentence,
            'options': options,
            'correct_answer': correct_index,
            'type': 'reverse_translation',
            'explanation': f"'{english_word}' translates to '{target_word}' in this context",
            'context': word.get('category', 'general')
        }
    
    def get_contextual_distractors(self, word: Dict, category: str) -> List[str]:
        """Generate contextually appropriate distractors"""
        # Get words from same category
        category_words = self.vocabulary_manager.words_by_category.get(category, [])
        distractors = [w['german'] for w in category_words 
                      if w['german'] != word['german']]
        
        if len(distractors) < 3:
            # Add words from similar categories
            similar_categories = ['general', 'basic', 'common']
            for cat in similar_categories:
                if cat in self.vocabulary_manager.words_by_category:
                    distractors.extend([w['german'] for w in self.vocabulary_manager.words_by_category[cat]
                                      if w['german'] != word['german']])
        
        return random.sample(distractors, min(3, len(distractors)))
    
    def get_phonetic_distractors(self, word: Dict) -> List[str]:
        """Generate phonetically similar distractors"""
        target = word['german'].lower()
        
        # Simple phonetic similarity (in real implementation, use phonetic algorithms)
        similar_words = []
        for vocab_word in self.vocabulary_manager.words:
            if vocab_word['german'] != word['german']:
                # Check for similar starting sounds, length, or patterns
                other = vocab_word['german'].lower()
                if (len(other) == len(target) or 
                    target[0] == other[0] or 
                    target[-1] == other[-1]):
                    similar_words.append(vocab_word['german'])
        
        return random.sample(similar_words, min(3, len(similar_words)))
    
    def get_semantic_distractors(self, word: Dict) -> List[str]:
        """Generate semantically related distractors"""
        category = word.get('category', 'general')
        level = word.get('level', 'A1')
        
        # Get words from same category and level
        candidates = []
        for vocab_word in self.vocabulary_manager.words:
            if (vocab_word['german'] != word['german'] and
                vocab_word.get('category') == category and
                vocab_word.get('level') == level):
                candidates.append(vocab_word['german'])
        
        if len(candidates) < 3:
            # Expand to same level, different category
            for vocab_word in self.vocabulary_manager.words:
                if (vocab_word['german'] != word['german'] and
                    vocab_word.get('level') == level):
                    candidates.append(vocab_word['german'])
        
        return random.sample(candidates, min(3, len(candidates)))
    
    def is_word_due_for_review(self, word_id: str) -> bool:
        """Check if word is due for spaced repetition review"""
        spaced_rep_data = self.user_progress.data.get('spaced_repetition', {})
        if word_id not in spaced_rep_data:
            return False
        
        next_review = spaced_rep_data[word_id].get('next_review')
        if not next_review:
            return False
        
        return datetime.fromisoformat(next_review) <= datetime.now()
    
    def get_recent_error_count(self, word_id: str) -> int:
        """Get recent error count for a word"""
        if not hasattr(self.user_progress, 'learning_analytics') or not self.user_progress.learning_analytics:
            return 0
        
        retention_data = self.user_progress.learning_analytics.analytics_data.get('retention_rates', {})
        if word_id not in retention_data:
            return 0
        
        # Simple error estimation based on retention rate
        retention_rate = retention_data[word_id].get('retention_rate', 100)
        tests_taken = retention_data[word_id].get('tests_taken', 0)
        
        if tests_taken == 0:
            return 0
        
        error_rate = (100 - retention_rate) / 100
        recent_errors = int(error_rate * min(tests_taken, 5))  # Last 5 tests
        
        return recent_errors
    
    def get_word_by_id(self, word_id: str) -> Optional[Dict]:
        """Get word data by German word ID"""
        for word in self.vocabulary_manager.words:
            if word['german'] == word_id:
                return word
        return None
    
    def process_adaptive_quiz_results(self, quiz_data: Dict, user_answers: List) -> Dict:
        """Process quiz results with adaptive feedback"""
        if not quiz_data or not quiz_data['questions']:
            return {'score': 0, 'total': 0}

        results = {
            'score': 0,
            'total': len(quiz_data['questions']),
            'detailed_results': [],
            'mastery_updates': [],
            'recommendations': []
        }

        for i, question in enumerate(quiz_data['questions']):
            word_id = question['word_id']
            is_correct = False

            if i < len(user_answers):
                if question['type'] == 'fill_in_blank':
                    # Check if answer matches (case-insensitive)
                    user_answer = str(user_answers[i]).strip().lower()
                    correct_answer = question.get('correct_answer', '').lower()
                    is_correct = user_answer == correct_answer
                else:
                    # Multiple choice
                    is_correct = user_answers[i] == question.get('correct_answer', -1)
            
            if is_correct:
                results['score'] += 1
            
            # Update word mastery and spaced repetition
            self.update_word_performance(word_id, is_correct, question.get('difficulty', 1))
            
            # Track detailed results
            results['detailed_results'].append({
                'word_id': word_id,
                'question_type': question['type'],
                'correct': is_correct,
                'difficulty': question.get('difficulty', 1),
                'mastery_before': question.get('mastery_level', 1)
            })
        
        # Calculate performance percentage
        results['percentage'] = (results['score'] / results['total']) * 100 if results['total'] > 0 else 0

        # Generate adaptive recommendations
        results['recommendations'] = self.generate_adaptive_recommendations(results)

        return results
    
    def update_word_performance(self, word_id: str, is_correct: bool, difficulty: int):
        """Update word performance tracking for adaptive learning"""
        # Update spaced repetition
        self.user_progress.update_review_result(word_id, is_correct)
        
        # Update analytics if available
        if hasattr(self.user_progress, 'learning_analytics') and self.user_progress.learning_analytics:
            retention_data = self.user_progress.learning_analytics.analytics_data.setdefault('retention_rates', {})
            
            if word_id not in retention_data:
                retention_data[word_id] = {
                    'tests_taken': 0,
                    'correct_answers': 0,
                    'retention_rate': 0.0,
                    'difficulty_history': []
                }
            
            word_data = retention_data[word_id]
            word_data['tests_taken'] += 1
            word_data['difficulty_history'].append(difficulty)
            
            if is_correct:
                word_data['correct_answers'] += 1
            
            # Update retention rate
            word_data['retention_rate'] = (word_data['correct_answers'] / word_data['tests_taken']) * 100
    
    def generate_adaptive_recommendations(self, results: Dict) -> List[str]:
        """Generate personalized recommendations based on quiz performance"""
        recommendations = []
        
        # Analyze performance by question type
        type_performance = {}
        for result in results['detailed_results']:
            q_type = result['question_type']
            if q_type not in type_performance:
                type_performance[q_type] = {'correct': 0, 'total': 0}
            
            type_performance[q_type]['total'] += 1
            if result['correct']:
                type_performance[q_type]['correct'] += 1
        
        # Generate recommendations based on weak areas
        for q_type, perf in type_performance.items():
            if perf['total'] > 0:
                accuracy = (perf['correct'] / perf['total']) * 100
                if accuracy < 60:
                    if q_type == 'fill_in_blank':
                        recommendations.append("Practice writing German words to improve spelling accuracy")
                    elif q_type == 'sentence_construction':
                        recommendations.append("Focus on German sentence structure and word order")
                    elif q_type == 'grammar_focus':
                        recommendations.append("Review German grammar rules and patterns")
                    elif q_type == 'contextual_usage':
                        recommendations.append("Practice using words in different contexts")
        
        # Overall performance recommendations
        if results['percentage'] < 70:
            recommendations.append("Review recently learned words more frequently")
        elif results['percentage'] > 90:
            recommendations.append("You're ready for more challenging question types!")
        
        return recommendations[:3]  # Limit to top 3 recommendations
