#!/usr/bin/env python3
"""
Interactive Quiz System for German Daily Word Bot
Provides spaced repetition quizzes and vocabulary reinforcement
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class QuizSystem:
    def __init__(self, vocabulary_manager, user_progress):
        self.vocabulary_manager = vocabulary_manager
        self.user_progress = user_progress
        self.quiz_types = [
            'translation_to_german',
            'translation_to_english', 
            'pronunciation_choice',
            'example_completion',
            'cultural_context'
        ]
    
    def should_send_quiz(self) -> bool:
        """Determine if a quiz should be sent today"""
        # Send quiz every 3 days or if user has 10+ learned words
        stats = self.user_progress.get_stats()
        streak = stats['daily_streak']
        total_words = stats['total_words_learned']
        
        return (streak % 3 == 0 and streak > 0) or total_words >= 10
    
    def generate_quiz(self, quiz_type: str = None, word_count: int = 5) -> Dict:
        """Generate a quiz based on learned vocabulary"""
        if not quiz_type:
            quiz_type = random.choice(self.quiz_types)
        
        # Get words for quiz (prioritize words due for review)
        review_words = self.user_progress.get_words_for_review()
        
        if len(review_words) < word_count:
            # Add recently learned words
            all_learned = []
            for level_data in self.user_progress.data['words_by_level'].values():
                for word_id in level_data['learned']:
                    word_data = self.get_word_by_id(word_id)
                    if word_data:
                        all_learned.append(word_data)
            
            # Combine and shuffle
            quiz_words = review_words + random.sample(
                all_learned, min(word_count - len(review_words), len(all_learned))
            )
        else:
            quiz_words = random.sample(review_words, word_count)
        
        if not quiz_words:
            return None
        
        # Generate quiz based on type
        quiz_data = {
            'type': quiz_type,
            'questions': [],
            'created_at': datetime.now().isoformat(),
            'user_level': self.user_progress.get_current_level()
        }
        
        for word in quiz_words:
            question = self.create_question(word, quiz_type)
            if question:
                quiz_data['questions'].append(question)
        
        return quiz_data
    
    def create_question(self, word: Dict, quiz_type: str) -> Optional[Dict]:
        """Create a single quiz question"""
        if quiz_type == 'translation_to_german':
            return self.create_translation_question(word, to_german=True)
        elif quiz_type == 'translation_to_english':
            return self.create_translation_question(word, to_german=False)
        elif quiz_type == 'pronunciation_choice':
            return self.create_pronunciation_question(word)
        elif quiz_type == 'example_completion':
            return self.create_example_completion_question(word)
        elif quiz_type == 'cultural_context':
            return self.create_cultural_question(word)
        
        return None
    
    def create_translation_question(self, word: Dict, to_german: bool) -> Dict:
        """Create a translation question"""
        if to_german:
            question_text = f"How do you say '{word['english']}' in German?"
            correct_answer = word['german']
            # Generate distractors from same level
            distractors = self.get_distractors(word, 'german', 3)
        else:
            question_text = f"What does '{word['german']}' mean in English?"
            correct_answer = word['english']
            distractors = self.get_distractors(word, 'english', 3)
        
        # Create multiple choice options
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        return {
            'word_id': word['german'],
            'question': question_text,
            'options': options,
            'correct_answer': correct_index,
            'explanation': f"'{word['german']}' means '{word['english']}'",
            'example': word['example'],
            'type': 'multiple_choice'
        }
    
    def create_pronunciation_question(self, word: Dict) -> Dict:
        """Create a pronunciation identification question"""
        question_text = f"Which is the correct pronunciation of '{word['german']}'?"
        correct_answer = word['pronunciation']
        
        # Generate fake pronunciations
        distractors = self.generate_fake_pronunciations(word['pronunciation'], 3)
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        return {
            'word_id': word['german'],
            'question': question_text,
            'options': options,
            'correct_answer': correct_index,
            'explanation': f"The correct pronunciation is {correct_answer}",
            'type': 'multiple_choice'
        }
    
    def create_example_completion_question(self, word: Dict) -> Dict:
        """Create a sentence completion question"""
        example = word['example']
        target_word = word['german']
        
        # Replace the target word with a blank
        if target_word in example:
            question_sentence = example.replace(target_word, "____", 1)
            question_text = f"Complete the sentence: {question_sentence}"
            
            # Generate distractors
            distractors = self.get_distractors(word, 'german', 3)
            options = [target_word] + distractors
            random.shuffle(options)
            correct_index = options.index(target_word)
            
            return {
                'word_id': word['german'],
                'question': question_text,
                'options': options,
                'correct_answer': correct_index,
                'explanation': f"Complete sentence: {example}",
                'translation': word['example_translation'],
                'type': 'multiple_choice'
            }
        
        return None
    
    def create_cultural_question(self, word: Dict) -> Optional[Dict]:
        """Create a cultural context question"""
        if 'cultural_note' not in word:
            return None
        
        cultural_note = word['cultural_note']
        question_text = f"When would you typically use '{word['german']}'?"
        
        # Create context-based options
        correct_answer = cultural_note
        distractors = [
            "Only in formal business settings",
            "Only with family members",
            "Only in written communication"
        ]
        
        options = [correct_answer] + distractors[:2]
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        return {
            'word_id': word['german'],
            'question': question_text,
            'options': options,
            'correct_answer': correct_index,
            'explanation': cultural_note,
            'type': 'multiple_choice'
        }
    
    def get_distractors(self, target_word: Dict, field: str, count: int) -> List[str]:
        """Generate distractor options for multiple choice questions"""
        level = target_word.get('level', 'A1')
        category = target_word.get('category', 'general')
        
        # Get words from same level and category
        same_level_words = self.vocabulary_manager.words_by_level.get(level, [])
        same_category_words = self.vocabulary_manager.words_by_category.get(category, [])
        
        # Combine and filter
        candidate_words = same_level_words + same_category_words
        candidates = [w[field] for w in candidate_words 
                     if w[field] != target_word[field] and w['german'] != target_word['german']]
        
        # Remove duplicates and select random distractors
        candidates = list(set(candidates))
        return random.sample(candidates, min(count, len(candidates)))
    
    def generate_fake_pronunciations(self, correct_pronunciation: str, count: int) -> List[str]:
        """Generate plausible but incorrect pronunciations"""
        # Simple approach: modify some phonetic elements
        fake_pronunciations = []
        
        # Common German phonetic substitutions for creating distractors
        substitutions = [
            ('ː', ''), ('ɐ', 'a'), ('ʊ', 'u'), ('ɪ', 'i'), 
            ('ɛ', 'e'), ('ɔ', 'o'), ('ʃ', 's'), ('ç', 'x')
        ]
        
        for i in range(count):
            fake = correct_pronunciation
            # Apply 1-2 random substitutions
            for _ in range(random.randint(1, 2)):
                old, new = random.choice(substitutions)
                fake = fake.replace(old, new, 1)
            
            if fake != correct_pronunciation and fake not in fake_pronunciations:
                fake_pronunciations.append(fake)
        
        # Fill remaining slots with more variations if needed
        while len(fake_pronunciations) < count:
            fake = correct_pronunciation.replace('/', '').replace('ˈ', '')
            fake_pronunciations.append(f"/{fake}/")
        
        return fake_pronunciations[:count]
    
    def get_word_by_id(self, word_id: str) -> Optional[Dict]:
        """Get word data by German word ID"""
        for word in self.vocabulary_manager.words:
            if word['german'] == word_id:
                return word
        return None
    
    def format_quiz_message(self, quiz_data: Dict) -> str:
        """Format quiz as Telegram message"""
        if not quiz_data or not quiz_data['questions']:
            return "No quiz available at this time."
        
        message = "🧠 **German Vocabulary Quiz**\n"
        message += f"📊 Level: {quiz_data['user_level']} | "
        message += f"Questions: {len(quiz_data['questions'])}\n"
        message += "=" * 40 + "\n\n"
        
        for i, question in enumerate(quiz_data['questions'], 1):
            message += f"**Question {i}:**\n"
            message += f"{question['question']}\n\n"
            
            for j, option in enumerate(question['options']):
                letter = chr(65 + j)  # A, B, C, D
                message += f"{letter}) {option}\n"
            
            message += f"\n💡 *Answer: {chr(65 + question['correct_answer'])}*\n"
            message += f"📝 {question['explanation']}\n"
            
            if 'example' in question:
                message += f"📖 Example: {question['example']}\n"
            
            message += "\n" + "-" * 30 + "\n\n"
        
        message += "🎯 **How did you do?** Review any words you missed!\n"
        message += "📚 Keep practicing to strengthen your German vocabulary!"
        
        return message
    
    def process_quiz_results(self, quiz_data: Dict, user_answers: List[int]) -> Dict:
        """Process quiz results and update spaced repetition"""
        if not quiz_data or not quiz_data['questions']:
            return {'score': 0, 'total': 0}
        
        correct_count = 0
        total_questions = len(quiz_data['questions'])
        
        for i, question in enumerate(quiz_data['questions']):
            if i < len(user_answers):
                is_correct = user_answers[i] == question['correct_answer']
                if is_correct:
                    correct_count += 1
                
                # Update spaced repetition for this word
                word_id = question['word_id']
                self.user_progress.update_review_result(word_id, is_correct)
        
        # Save updated progress
        self.user_progress.save_progress()
        
        score_percentage = (correct_count / total_questions) * 100
        
        return {
            'score': correct_count,
            'total': total_questions,
            'percentage': score_percentage,
            'passed': score_percentage >= 70
        }
