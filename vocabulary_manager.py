#!/usr/bin/env python3
"""
Enhanced Vocabulary Manager for German Daily Word Bot
Handles CEFR level progression, word selection, and learning optimization
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class VocabularyManager:
    def __init__(self, words_file: str = 'words.json'):
        self.words_file = words_file
        self.words = self.load_words()
        self.words_by_level = self.organize_by_level()
        self.words_by_category = self.organize_by_category()
    
    def load_words(self) -> List[Dict]:
        """Load vocabulary database from JSON file"""
        try:
            with open(self.words_file, 'r', encoding='utf-8') as f:
                words = json.load(f)
            logger.info(f"Loaded {len(words)} words from vocabulary database")
            return words
        except FileNotFoundError:
            logger.error(f"Vocabulary file {self.words_file} not found")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing {self.words_file}: {e}")
            raise
    
    def organize_by_level(self) -> Dict[str, List[Dict]]:
        """Organize words by CEFR level"""
        levels = {'A1': [], 'A2': [], 'B1': [], 'B2': []}
        
        for word in self.words:
            level = word.get('level', 'A1')  # Default to A1 if no level specified
            if level in levels:
                levels[level].append(word)
        
        logger.info(f"Words by level: {[(level, len(words)) for level, words in levels.items()]}")
        return levels
    
    def organize_by_category(self) -> Dict[str, List[Dict]]:
        """Organize words by category"""
        categories = {}
        
        for word in self.words:
            category = word.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(word)
        
        return categories
    
    def get_words_for_level(self, level: str, count: int, 
                           exclude_words: List[str] = None,
                           preferred_categories: List[str] = None) -> List[Dict]:
        """Get words for specific CEFR level with smart selection"""
        if level not in self.words_by_level:
            logger.warning(f"Level {level} not found, defaulting to A1")
            level = 'A1'
        
        available_words = self.words_by_level[level].copy()
        exclude_words = exclude_words or []
        
        # Filter out already learned words
        available_words = [w for w in available_words if w['german'] not in exclude_words]
        
        if not available_words:
            logger.warning(f"No available words for level {level}")
            return []
        
        # Prioritize preferred categories if specified
        if preferred_categories:
            preferred_words = [w for w in available_words if w['category'] in preferred_categories]
            if preferred_words:
                available_words = preferred_words
        
        # Sort by frequency (lower number = more common/important)
        available_words.sort(key=lambda x: x.get('frequency', 999))
        
        # Select words with some randomization but bias toward high-frequency words
        selected_words = []
        
        # Take top 50% most frequent words for selection pool
        pool_size = max(count * 3, len(available_words) // 2)
        selection_pool = available_words[:pool_size]
        
        # Randomly select from the pool
        selected_count = min(count, len(selection_pool))
        selected_words = random.sample(selection_pool, selected_count)
        
        logger.info(f"Selected {len(selected_words)} words for level {level}")
        return selected_words
    
    def get_progressive_words(self, user_level: str, count: int, 
                            learned_words: List[str] = None) -> List[Dict]:
        """Get words with progressive difficulty mixing"""
        learned_words = learned_words or []
        
        # Progressive mixing strategy
        level_distribution = {
            'A1': {'A1': 1.0},  # 100% A1 words
            'A2': {'A1': 0.3, 'A2': 0.7},  # 30% A1 review, 70% A2 new
            'B1': {'A1': 0.1, 'A2': 0.3, 'B1': 0.6},  # Mixed levels
            'B2': {'A1': 0.1, 'A2': 0.2, 'B1': 0.3, 'B2': 0.4}  # Mostly advanced
        }
        
        if user_level not in level_distribution:
            user_level = 'A1'
        
        distribution = level_distribution[user_level]
        selected_words = []
        
        for level, ratio in distribution.items():
            level_count = max(1, int(count * ratio))
            level_words = self.get_words_for_level(
                level, level_count, learned_words
            )
            selected_words.extend(level_words)
        
        # Ensure we don't exceed the requested count
        if len(selected_words) > count:
            selected_words = selected_words[:count]
        
        # Fill up to count if we're short
        while len(selected_words) < count:
            additional_words = self.get_words_for_level(
                user_level, count - len(selected_words), 
                learned_words + [w['german'] for w in selected_words]
            )
            if not additional_words:
                break
            selected_words.extend(additional_words)
        
        return selected_words[:count]
    
    def get_review_words(self, learned_words: List[str], count: int) -> List[Dict]:
        """Get words for review from previously learned vocabulary"""
        review_candidates = [w for w in self.words if w['german'] in learned_words]
        
        if not review_candidates:
            return []
        
        # Prioritize words that haven't been reviewed recently
        # For now, just random selection
        review_count = min(count, len(review_candidates))
        return random.sample(review_candidates, review_count)
    
    def get_thematic_words(self, theme: str, level: str, count: int) -> List[Dict]:
        """Get words for specific theme/topic"""
        theme_words = []
        
        # Map themes to categories
        theme_mapping = {
            'daily_life': ['food_drink', 'home', 'family', 'time'],
            'travel': ['transport', 'directions', 'accommodation', 'weather'],
            'business': ['work', 'office', 'meetings', 'technology'],
            'social': ['greetings', 'politeness', 'emotions', 'relationships']
        }
        
        categories = theme_mapping.get(theme, [theme])
        
        for category in categories:
            if category in self.words_by_category:
                category_words = [w for w in self.words_by_category[category] 
                                if w.get('level') == level]
                theme_words.extend(category_words)
        
        if not theme_words:
            # Fallback to regular level-based selection
            return self.get_words_for_level(level, count)
        
        return random.sample(theme_words, min(count, len(theme_words)))
    
    def get_grammar_tip(self, words: List[Dict]) -> Optional[str]:
        """Generate grammar tip based on selected words"""
        if not words:
            return None
        
        # Analyze word types in the selection
        word_types = [w.get('word_type', 'unknown') for w in words]
        
        grammar_tips = {
            'noun': [
                "🔤 German nouns are always capitalized and have grammatical gender (der/die/das).",
                "📝 Tip: Learn the article with the noun - 'der Hund', 'die Katze', 'das Haus'.",
                "🎯 German has four cases: Nominativ, Akkusativ, Dativ, Genitiv. Start with Nominativ!"
            ],
            'verb': [
                "🔄 German verbs change their endings based on who is doing the action.",
                "📚 Regular verbs follow patterns: ich lerne, du lernst, er/sie/es lernt.",
                "⚡ Separable verbs split in sentences: 'Ich stehe um 7 Uhr auf' (aufstehen)."
            ],
            'adjective': [
                "🎨 German adjectives change endings when used before nouns.",
                "📏 Adjective endings depend on gender, case, and article type.",
                "💡 After 'sein' (to be), adjectives don't change: 'Das Haus ist groß'."
            ]
        }
        
        # Find the most common word type
        most_common_type = max(set(word_types), key=word_types.count) if word_types else 'noun'
        
        if most_common_type in grammar_tips:
            return random.choice(grammar_tips[most_common_type])
        
        # Default grammar tips
        general_tips = [
            "🇩🇪 German word order: Subject-Verb-Object in main clauses.",
            "📖 Practice makes perfect! Try to use new words in your own sentences.",
            "🎵 German pronunciation is quite regular - what you see is what you say!",
            "🔗 Connect new words to words you already know to build vocabulary networks."
        ]
        
        return random.choice(general_tips)
    
    def validate_database(self) -> Dict[str, any]:
        """Validate vocabulary database structure and content"""
        required_fields = ['german', 'english', 'pronunciation', 'example', 
                          'example_translation', 'category', 'level']
        
        validation_results = {
            'total_words': len(self.words),
            'missing_fields': [],
            'level_distribution': {},
            'category_distribution': {},
            'errors': []
        }
        
        # Count level distribution
        for level in ['A1', 'A2', 'B1', 'B2']:
            validation_results['level_distribution'][level] = len(self.words_by_level.get(level, []))
        
        # Count category distribution
        validation_results['category_distribution'] = {
            cat: len(words) for cat, words in self.words_by_category.items()
        }
        
        # Check for missing fields
        for i, word in enumerate(self.words):
            for field in required_fields:
                if field not in word or not word[field]:
                    validation_results['missing_fields'].append(f"Word {i+1}: missing {field}")
        
        return validation_results
