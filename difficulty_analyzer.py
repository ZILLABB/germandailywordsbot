#!/usr/bin/env python3
"""
Word Difficulty Analyzer for German Daily Word Bot
Analyzes and scores word difficulty based on multiple linguistic factors
"""

import re
import math
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DifficultyAnalyzer:
    def __init__(self, vocabulary_manager):
        self.vocabulary_manager = vocabulary_manager
        
        # Difficulty factors and weights
        self.difficulty_weights = {
            'length': 0.15,           # Word length
            'phonetic_complexity': 0.20,  # Pronunciation difficulty
            'frequency': 0.25,        # Usage frequency (inverse)
            'grammar_complexity': 0.15,   # Grammatical complexity
            'cognate_similarity': 0.10,   # Similarity to English
            'syllable_count': 0.10,   # Number of syllables
            'special_characters': 0.05    # Umlauts, ß, etc.
        }
        
        # Common German phonetic patterns (simplified)
        self.difficult_sounds = [
            'ç', 'x', 'ʃ', 'ʒ', 'ɔɪ', 'aɪ', 'aʊ', 'ʏ', 'œ', 'ɛː', 'øː'
        ]
        
        # Common English-German cognates for similarity analysis
        self.cognate_patterns = [
            ('tion', 'tion'), ('ly', 'lich'), ('er', 'er'), ('ing', 'ung'),
            ('ful', 'voll'), ('less', 'los'), ('ness', 'heit')
        ]
        
        # Grammar complexity indicators
        self.complex_grammar = {
            'separable_verbs': ['ab', 'an', 'auf', 'aus', 'bei', 'ein', 'mit', 'nach', 'vor', 'zu'],
            'modal_verbs': ['können', 'müssen', 'sollen', 'wollen', 'dürfen', 'mögen'],
            'irregular_verbs': ['sein', 'haben', 'werden', 'gehen', 'kommen', 'sehen', 'wissen']
        }
    
    def analyze_word_difficulty(self, word: Dict) -> Dict:
        """Comprehensive difficulty analysis for a word"""
        german_word = word['german']
        english_word = word['english']
        
        analysis = {
            'word': german_word,
            'overall_difficulty': 0.0,
            'difficulty_level': 'Easy',
            'factors': {}
        }
        
        # Calculate individual difficulty factors
        analysis['factors']['length'] = self.calculate_length_difficulty(german_word)
        analysis['factors']['phonetic_complexity'] = self.calculate_phonetic_difficulty(word)
        analysis['factors']['frequency'] = self.calculate_frequency_difficulty(word)
        analysis['factors']['grammar_complexity'] = self.calculate_grammar_difficulty(word)
        analysis['factors']['cognate_similarity'] = self.calculate_cognate_similarity(german_word, english_word)
        analysis['factors']['syllable_count'] = self.calculate_syllable_difficulty(german_word)
        analysis['factors']['special_characters'] = self.calculate_special_char_difficulty(german_word)
        
        # Calculate weighted overall difficulty
        total_difficulty = 0.0
        for factor, score in analysis['factors'].items():
            weight = self.difficulty_weights.get(factor, 0.1)
            total_difficulty += score * weight
        
        analysis['overall_difficulty'] = min(10.0, max(1.0, total_difficulty))
        analysis['difficulty_level'] = self.get_difficulty_level(analysis['overall_difficulty'])
        
        return analysis
    
    def calculate_length_difficulty(self, word: str) -> float:
        """Calculate difficulty based on word length"""
        length = len(word)
        
        if length <= 4:
            return 1.0
        elif length <= 7:
            return 3.0
        elif length <= 10:
            return 6.0
        else:
            return 9.0
    
    def calculate_phonetic_difficulty(self, word: Dict) -> float:
        """Calculate difficulty based on pronunciation complexity"""
        pronunciation = word.get('pronunciation', '')
        
        if not pronunciation:
            # Estimate based on German word patterns
            german_word = word['german'].lower()
            difficulty = 3.0  # Base difficulty
            
            # Check for difficult letter combinations
            difficult_patterns = ['sch', 'tsch', 'pf', 'tz', 'ch', 'ck', 'qu']
            for pattern in difficult_patterns:
                if pattern in german_word:
                    difficulty += 1.0
            
            # Check for umlauts and special characters
            special_chars = ['ä', 'ö', 'ü', 'ß']
            for char in special_chars:
                if char in german_word:
                    difficulty += 0.5
            
            return min(10.0, difficulty)
        
        # Analyze IPA pronunciation
        difficulty = 2.0  # Base difficulty
        
        for sound in self.difficult_sounds:
            if sound in pronunciation:
                difficulty += 1.5
        
        # Count stress marks and length markers
        stress_markers = pronunciation.count('ˈ') + pronunciation.count('ˌ')
        length_markers = pronunciation.count('ː')
        
        difficulty += stress_markers * 0.5 + length_markers * 0.3
        
        return min(10.0, difficulty)
    
    def calculate_frequency_difficulty(self, word: Dict) -> float:
        """Calculate difficulty based on word frequency (inverse relationship)"""
        frequency = word.get('frequency', 5)  # Default to medium frequency
        
        # Convert frequency to difficulty (higher frequency = lower difficulty)
        if frequency == 1:  # Very common
            return 1.0
        elif frequency <= 3:  # Common
            return 3.0
        elif frequency <= 6:  # Medium
            return 5.0
        elif frequency <= 8:  # Uncommon
            return 7.0
        else:  # Rare
            return 9.0
    
    def calculate_grammar_difficulty(self, word: Dict) -> float:
        """Calculate difficulty based on grammatical complexity"""
        word_type = word.get('word_type', 'noun')
        german_word = word['german']
        
        difficulty = 2.0  # Base difficulty
        
        if word_type == 'verb':
            # Check for separable verbs
            for prefix in self.complex_grammar['separable_verbs']:
                if german_word.startswith(prefix):
                    difficulty += 2.0
                    break
            
            # Check for modal verbs
            if german_word in self.complex_grammar['modal_verbs']:
                difficulty += 1.5
            
            # Check for irregular verbs
            if german_word in self.complex_grammar['irregular_verbs']:
                difficulty += 2.0
        
        elif word_type == 'noun':
            # Compound nouns are more difficult
            if len(german_word) > 10 and german_word[0].isupper():
                difficulty += 1.5
            
            # Check for multiple capital letters (compound indicator)
            capital_count = sum(1 for c in german_word if c.isupper())
            if capital_count > 1:
                difficulty += 1.0
        
        elif word_type == 'adjective':
            # Adjectives with complex endings
            complex_endings = ['lich', 'isch', 'haft', 'sam', 'bar']
            for ending in complex_endings:
                if german_word.endswith(ending):
                    difficulty += 1.0
                    break
        
        return min(10.0, difficulty)
    
    def calculate_cognate_similarity(self, german_word: str, english_word: str) -> float:
        """Calculate difficulty based on similarity to English (cognates)"""
        # Direct similarity check
        similarity_ratio = self.calculate_string_similarity(german_word.lower(), english_word.lower())
        
        # Check for cognate patterns
        pattern_bonus = 0.0
        for ger_pattern, eng_pattern in self.cognate_patterns:
            if german_word.endswith(ger_pattern) and english_word.endswith(eng_pattern):
                pattern_bonus = 2.0
                break
        
        # Higher similarity = lower difficulty
        base_difficulty = 8.0
        similarity_reduction = similarity_ratio * 6.0 + pattern_bonus
        
        return max(1.0, base_difficulty - similarity_reduction)
    
    def calculate_syllable_difficulty(self, word: str) -> float:
        """Calculate difficulty based on syllable count"""
        syllable_count = self.count_syllables(word)
        
        if syllable_count <= 1:
            return 1.0
        elif syllable_count <= 2:
            return 2.0
        elif syllable_count <= 3:
            return 4.0
        elif syllable_count <= 4:
            return 6.0
        else:
            return 8.0
    
    def calculate_special_char_difficulty(self, word: str) -> float:
        """Calculate difficulty based on special German characters"""
        special_chars = ['ä', 'ö', 'ü', 'ß']
        count = sum(1 for char in word.lower() if char in special_chars)
        
        return min(5.0, count * 1.5)
    
    def count_syllables(self, word: str) -> int:
        """Estimate syllable count for German word"""
        word = word.lower()
        vowels = 'aeiouäöü'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Adjust for common German patterns
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using Levenshtein distance"""
        if len(str1) == 0:
            return 0.0 if len(str2) == 0 else 1.0
        if len(str2) == 0:
            return 1.0
        
        # Create matrix
        matrix = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]
        
        # Initialize first row and column
        for i in range(len(str1) + 1):
            matrix[i][0] = i
        for j in range(len(str2) + 1):
            matrix[0][j] = j
        
        # Fill matrix
        for i in range(1, len(str1) + 1):
            for j in range(1, len(str2) + 1):
                if str1[i-1] == str2[j-1]:
                    cost = 0
                else:
                    cost = 1
                
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )
        
        # Calculate similarity ratio
        max_len = max(len(str1), len(str2))
        distance = matrix[len(str1)][len(str2)]
        similarity = 1.0 - (distance / max_len)
        
        return max(0.0, similarity)
    
    def get_difficulty_level(self, score: float) -> str:
        """Convert numerical difficulty score to level"""
        if score <= 2.5:
            return 'Very Easy'
        elif score <= 4.0:
            return 'Easy'
        elif score <= 6.0:
            return 'Medium'
        elif score <= 7.5:
            return 'Hard'
        else:
            return 'Very Hard'
    
    def analyze_vocabulary_difficulty_distribution(self) -> Dict:
        """Analyze difficulty distribution across entire vocabulary"""
        difficulty_counts = {
            'Very Easy': 0,
            'Easy': 0,
            'Medium': 0,
            'Hard': 0,
            'Very Hard': 0
        }
        
        total_words = 0
        difficulty_sum = 0.0
        
        for word in self.vocabulary_manager.words:
            analysis = self.analyze_word_difficulty(word)
            difficulty_level = analysis['difficulty_level']
            difficulty_score = analysis['overall_difficulty']
            
            difficulty_counts[difficulty_level] += 1
            difficulty_sum += difficulty_score
            total_words += 1
        
        return {
            'distribution': difficulty_counts,
            'average_difficulty': difficulty_sum / total_words if total_words > 0 else 0,
            'total_words': total_words,
            'difficulty_percentages': {
                level: (count / total_words) * 100 if total_words > 0 else 0
                for level, count in difficulty_counts.items()
            }
        }
    
    def get_words_by_difficulty_range(self, min_difficulty: float, max_difficulty: float) -> List[Dict]:
        """Get words within a specific difficulty range"""
        matching_words = []
        
        for word in self.vocabulary_manager.words:
            analysis = self.analyze_word_difficulty(word)
            if min_difficulty <= analysis['overall_difficulty'] <= max_difficulty:
                word_with_difficulty = word.copy()
                word_with_difficulty['difficulty_analysis'] = analysis
                matching_words.append(word_with_difficulty)
        
        # Sort by difficulty
        matching_words.sort(key=lambda w: w['difficulty_analysis']['overall_difficulty'])
        
        return matching_words
    
    def recommend_next_difficulty_level(self, user_progress) -> Dict:
        """Recommend appropriate difficulty level for user"""
        stats = user_progress.get_stats()
        total_words = stats['total_words_learned']
        current_level = stats['current_level']
        
        # Get recent quiz performance
        quiz_scores = user_progress.data.get('quiz_scores', [])
        if quiz_scores:
            recent_scores = quiz_scores[-5:]  # Last 5 quizzes
            avg_performance = sum(q['percentage'] for q in recent_scores) / len(recent_scores)
        else:
            avg_performance = 0
        
        # Determine recommended difficulty range
        if total_words < 20 or avg_performance < 60:
            recommended_range = (1.0, 3.0)
            level_name = "Beginner"
        elif total_words < 50 or avg_performance < 75:
            recommended_range = (2.0, 5.0)
            level_name = "Elementary"
        elif total_words < 100 or avg_performance < 85:
            recommended_range = (3.0, 7.0)
            level_name = "Intermediate"
        else:
            recommended_range = (5.0, 10.0)
            level_name = "Advanced"
        
        # Get words in recommended range
        suitable_words = self.get_words_by_difficulty_range(
            recommended_range[0], recommended_range[1]
        )
        
        return {
            'recommended_difficulty_range': recommended_range,
            'level_name': level_name,
            'suitable_word_count': len(suitable_words),
            'user_performance': avg_performance,
            'total_words_learned': total_words,
            'current_cefr_level': current_level
        }
    
    def create_adaptive_word_selection(self, user_progress, word_count: int = 3) -> List[Dict]:
        """Select words adaptively based on user's current ability"""
        recommendation = self.recommend_next_difficulty_level(user_progress)
        difficulty_range = recommendation['recommended_difficulty_range']
        
        # Get suitable words
        suitable_words = self.get_words_by_difficulty_range(
            difficulty_range[0], difficulty_range[1]
        )
        
        # Filter out already learned words
        learned_words = []
        for level_data in user_progress.data['words_by_level'].values():
            learned_words.extend(level_data['learned'])
        
        unlearned_words = [w for w in suitable_words if w['german'] not in learned_words]
        
        # Select words with variety in difficulty
        if len(unlearned_words) >= word_count:
            # Sort by difficulty and select spread
            unlearned_words.sort(key=lambda w: w['difficulty_analysis']['overall_difficulty'])
            
            selected_words = []
            step = len(unlearned_words) // word_count
            
            for i in range(word_count):
                index = min(i * step, len(unlearned_words) - 1)
                selected_words.append(unlearned_words[index])
            
            return selected_words
        else:
            return unlearned_words[:word_count]
