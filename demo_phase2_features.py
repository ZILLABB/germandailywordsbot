#!/usr/bin/env python3
"""
Demo Script for Phase 2: Interactive Assessment System
Demonstrates adaptive quizzes, difficulty analysis, and mastery-based progression
"""

import os
import json
import logging
from datetime import datetime

# Import Phase 2 modules
try:
    from user_progress import UserProgress
    from vocabulary_manager import VocabularyManager
    from adaptive_quiz_system import AdaptiveQuizSystem
    from difficulty_analyzer import DifficultyAnalyzer
    from enhanced_quiz_system import EnhancedQuizSystem
    PHASE2_AVAILABLE = True
except ImportError as e:
    print(f"Phase 2 modules not available: {e}")
    PHASE2_AVAILABLE = False
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class Phase2Demo:
    def __init__(self):
        self.demo_chat_id = "phase2_demo_user"
        self.vocabulary_manager = VocabularyManager()
        
        # Clean up any existing demo data
        self.cleanup_demo_data()
        
        print("🧠 German Daily Word Bot - Phase 2: Interactive Assessment Demo")
        print("=" * 70)
    
    def cleanup_demo_data(self):
        """Clean up any existing demo data"""
        demo_file = f"progress_{self.demo_chat_id}.json"
        if os.path.exists(demo_file):
            os.remove(demo_file)
    
    def run_demo(self):
        """Run comprehensive Phase 2 demonstration"""
        print("\n🎯 DEMONSTRATING INTERACTIVE ASSESSMENT SYSTEM")
        print("-" * 60)
        
        # 1. Word Difficulty Analysis
        self.demo_difficulty_analysis()
        
        # 2. Adaptive Quiz System
        self.demo_adaptive_quiz_system()
        
        # 3. Enhanced Quiz Types
        self.demo_enhanced_quiz_types()
        
        # 4. Mastery-Based Progression
        self.demo_mastery_progression()
        
        # 5. Intelligent Word Selection
        self.demo_intelligent_selection()
        
        # 6. Complete Enhanced Quiz Experience
        self.demo_complete_experience()
        
        print("\n🎉 PHASE 2 DEMO COMPLETE!")
        print("Interactive Assessment System is fully operational!")
        
        # Cleanup
        self.cleanup_demo_data()
    
    def demo_difficulty_analysis(self):
        """Demonstrate word difficulty analysis"""
        print("\n1️⃣ WORD DIFFICULTY ANALYSIS")
        print("   Analyzing vocabulary complexity with 7 linguistic factors...")
        
        difficulty_analyzer = DifficultyAnalyzer(self.vocabulary_manager)
        
        # Analyze different complexity words
        test_words = [
            {'german': 'Hallo', 'english': 'Hello', 'pronunciation': '/haˈloː/', 'category': 'greetings'},
            {'german': 'Schwierigkeitsgrad', 'english': 'Difficulty level', 'pronunciation': '/ˈʃviːʁɪçkaɪtsˌɡʁaːt/', 'category': 'academic'},
            {'german': 'Wasser', 'english': 'Water', 'pronunciation': '/ˈvasɐ/', 'category': 'food_drink'}
        ]
        
        for word in test_words:
            analysis = difficulty_analyzer.analyze_word_difficulty(word)
            print(f"   📊 {word['german']}: {analysis['overall_difficulty']:.1f}/10 ({analysis['difficulty_level']})")
            
            # Show key factors
            factors = analysis['factors']
            print(f"      Length: {factors['length']:.1f}, Phonetic: {factors['phonetic_complexity']:.1f}, "
                  f"Frequency: {factors['frequency']:.1f}")
        
        # Show vocabulary distribution
        distribution = difficulty_analyzer.analyze_vocabulary_difficulty_distribution()
        print(f"   📈 Vocabulary Distribution:")
        for level, percentage in distribution['difficulty_percentages'].items():
            if percentage > 0:
                print(f"      {level}: {percentage:.1f}%")
    
    def demo_adaptive_quiz_system(self):
        """Demonstrate adaptive quiz system"""
        print("\n2️⃣ ADAPTIVE QUIZ SYSTEM")
        print("   Creating intelligent, personalized quizzes...")
        
        user_progress = UserProgress(self.demo_chat_id, self.vocabulary_manager)
        adaptive_quiz = AdaptiveQuizSystem(self.vocabulary_manager, user_progress)
        
        # Add learned words
        learned_words = [
            {'german': 'Hallo', 'english': 'Hello', 'level': 'A1'},
            {'german': 'Danke', 'english': 'Thank you', 'level': 'A1'},
            {'german': 'Wasser', 'english': 'Water', 'level': 'A1'},
            {'german': 'Schwierig', 'english': 'Difficult', 'level': 'A2'}
        ]
        
        for word in learned_words:
            user_progress.add_learned_word(word)
        
        # Show adaptive features
        difficulty_level = adaptive_quiz.get_user_difficulty_level()
        quiz_types = adaptive_quiz.get_adaptive_quiz_types()
        
        print(f"   🎯 User Difficulty Level: {difficulty_level}")
        print(f"   🧩 Available Quiz Types: {len(quiz_types)} types")
        print(f"      {', '.join(quiz_types[:4])}...")
        
        # Generate adaptive quiz
        quiz_data = adaptive_quiz.generate_adaptive_quiz(word_count=3)
        if quiz_data:
            print(f"   ✅ Generated adaptive quiz with {len(quiz_data['questions'])} questions")
            print(f"   📊 Quiz Type: {quiz_data['type']}")
            print(f"   🎓 Target Level: {quiz_data['user_level']}")
    
    def demo_enhanced_quiz_types(self):
        """Demonstrate enhanced quiz question types"""
        print("\n3️⃣ ENHANCED QUIZ TYPES")
        print("   Showcasing 6 different question formats...")
        
        user_progress = UserProgress(self.demo_chat_id, self.vocabulary_manager)
        adaptive_quiz = AdaptiveQuizSystem(self.vocabulary_manager, user_progress)
        
        test_word = {
            'german': 'Wasser',
            'english': 'Water',
            'example': 'Ich trinke Wasser.',
            'category': 'food_drink',
            'level': 'A1'
        }
        
        question_types = [
            ('fill_in_blank', 'Fill-in-the-Blank'),
            ('sentence_construction', 'Sentence Construction'),
            ('contextual_usage', 'Contextual Usage'),
            ('grammar_focus', 'Grammar Focus'),
            ('audio_recognition', 'Audio Recognition'),
            ('reverse_translation', 'Reverse Translation')
        ]
        
        for q_type, display_name in question_types:
            try:
                question = adaptive_quiz.create_adaptive_question(test_word, q_type)
                if question:
                    print(f"   ✅ {display_name}: Generated successfully")
                    # Show preview of question
                    preview = question['question'][:50] + "..." if len(question['question']) > 50 else question['question']
                    print(f"      Preview: {preview}")
                else:
                    print(f"   ❌ {display_name}: Generation failed")
            except Exception as e:
                print(f"   ⚠️  {display_name}: {str(e)[:30]}...")
    
    def demo_mastery_progression(self):
        """Demonstrate mastery-based progression"""
        print("\n4️⃣ MASTERY-BASED PROGRESSION")
        print("   Tracking skill development with 5-level mastery system...")
        
        user_progress = UserProgress(self.demo_chat_id, self.vocabulary_manager)
        adaptive_quiz = AdaptiveQuizSystem(self.vocabulary_manager, user_progress)
        
        # Simulate word mastery levels
        test_words = ['Hallo', 'Danke', 'Wasser', 'Schwierig']
        
        print("   📊 Word Mastery Levels:")
        for word in test_words:
            mastery = adaptive_quiz.get_word_mastery_level(word)
            mastery_name = adaptive_quiz.mastery_levels.get(mastery, 'Unknown')
            print(f"      {word}: Level {mastery} ({mastery_name})")
        
        # Simulate quiz results processing
        test_quiz_data = {
            'questions': [
                {'word_id': 'Hallo', 'type': 'translation', 'difficulty': 1, 'correct_answer': 0},
                {'word_id': 'Wasser', 'type': 'fill_in_blank', 'difficulty': 2, 'correct_answer': 'Wasser'}
            ]
        }
        
        user_answers = [0, 'wasser']  # Simulate answers
        results = adaptive_quiz.process_adaptive_quiz_results(test_quiz_data, user_answers)
        
        print(f"   🎯 Quiz Results: {results['score']}/{results['total']} ({results['percentage']:.1f}%)")
        print(f"   💡 Recommendations: {len(results['recommendations'])} generated")
        if results['recommendations']:
            print(f"      Example: {results['recommendations'][0]}")
    
    def demo_intelligent_selection(self):
        """Demonstrate intelligent word selection"""
        print("\n5️⃣ INTELLIGENT WORD SELECTION")
        print("   Smart word prioritization for optimal learning...")
        
        user_progress = UserProgress(self.demo_chat_id, self.vocabulary_manager)
        adaptive_quiz = AdaptiveQuizSystem(self.vocabulary_manager, user_progress)
        difficulty_analyzer = DifficultyAnalyzer(self.vocabulary_manager)
        
        # Add multiple learned words
        learned_words = [
            {'german': 'Hallo', 'english': 'Hello', 'level': 'A1'},
            {'german': 'Danke', 'english': 'Thank you', 'level': 'A1'},
            {'german': 'Wasser', 'english': 'Water', 'level': 'A1'},
            {'german': 'Brot', 'english': 'Bread', 'level': 'A1'},
            {'german': 'Haus', 'english': 'House', 'level': 'A1'}
        ]
        
        for word in learned_words:
            user_progress.add_learned_word(word)
        
        # Demonstrate intelligent selection
        selected_words = adaptive_quiz.select_words_for_quiz(word_count=3)
        print(f"   🎯 Intelligently Selected Words: {len(selected_words)}")
        for word in selected_words:
            print(f"      {word['german']} ({word['english']})")
        
        # Show difficulty recommendation
        recommendation = difficulty_analyzer.recommend_next_difficulty_level(user_progress)
        print(f"   📊 Recommended Difficulty: {recommendation['level_name']}")
        print(f"   📈 Difficulty Range: {recommendation['recommended_difficulty_range']}")
        print(f"   📚 Suitable Words Available: {recommendation['suitable_word_count']}")
    
    def demo_complete_experience(self):
        """Demonstrate complete enhanced quiz experience"""
        print("\n6️⃣ COMPLETE ENHANCED QUIZ EXPERIENCE")
        print("   Full integration of all Phase 2 features...")
        
        user_progress = UserProgress(self.demo_chat_id, self.vocabulary_manager)
        enhanced_quiz = EnhancedQuizSystem(self.vocabulary_manager, user_progress)
        
        # Add learned words
        learned_words = [
            {'german': 'Hallo', 'english': 'Hello', 'level': 'A1'},
            {'german': 'Danke', 'english': 'Thank you', 'level': 'A1'},
            {'german': 'Wasser', 'english': 'Water', 'level': 'A1'}
        ]
        
        for word in learned_words:
            user_progress.add_learned_word(word)
        
        # Test different quiz modes
        quiz_modes = [
            ('adaptive', 'Adaptive Mixed Quiz'),
            ('mastery_focused', 'Mastery-Focused Quiz'),
            ('difficulty_progressive', 'Progressive Difficulty Quiz'),
            ('weak_areas', 'Weak Areas Focus Quiz')
        ]
        
        print("   🧩 Enhanced Quiz Modes:")
        for mode, description in quiz_modes:
            try:
                quiz_data = enhanced_quiz.generate_enhanced_quiz(mode, word_count=2)
                if quiz_data and quiz_data.get('questions'):
                    print(f"   ✅ {description}: {len(quiz_data['questions'])} questions")
                    print(f"      Focus: {quiz_data.get('focus', 'General')}")
                else:
                    print(f"   ⚠️  {description}: No questions generated")
            except Exception as e:
                print(f"   ❌ {description}: Error - {str(e)[:30]}...")
        
        # Show performance level detection
        performance_level = enhanced_quiz.get_user_performance_level()
        print(f"   📊 User Performance Level: {performance_level}")
        
        # Show quiz scheduling intelligence
        should_send = enhanced_quiz.should_send_enhanced_quiz()
        print(f"   ⏰ Should Send Quiz Today: {should_send}")
        
        # Generate sample quiz message
        sample_quiz = enhanced_quiz.generate_enhanced_quiz('adaptive', word_count=2)
        if sample_quiz:
            message = enhanced_quiz.format_enhanced_quiz_message(sample_quiz)
            print(f"   📱 Generated Quiz Message: {len(message)} characters")
            print(f"   📝 Message Preview:")
            lines = message.split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"      {line[:60]}{'...' if len(line) > 60 else ''}")

def main():
    """Main function to run Phase 2 demo"""
    try:
        demo = Phase2Demo()
        demo.run_demo()
        return True
        
    except Exception as e:
        logger.error(f"Error running Phase 2 demo: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
