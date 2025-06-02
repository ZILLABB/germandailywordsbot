#!/usr/bin/env python3
"""
Test Script for Phase 2: Interactive Assessment System
Tests adaptive quizzes, difficulty analysis, and mastery-based progression
"""

import os
import json
import logging
from datetime import datetime, timedelta

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase2TestSuite:
    def __init__(self):
        self.test_chat_id = "phase2_test_789"
        self.vocabulary_manager = VocabularyManager()
        self.test_results = []
        
        # Clean up any existing test data
        self.cleanup_test_data()
        
        logger.info("Phase 2 Test Suite initialized")
    
    def cleanup_test_data(self):
        """Clean up any existing test data"""
        test_file = f"progress_{self.test_chat_id}.json"
        if os.path.exists(test_file):
            os.remove(test_file)
            logger.info("Cleaned up existing test data")
    
    def run_all_tests(self):
        """Run all Phase 2 tests"""
        logger.info("Starting Phase 2: Interactive Assessment System tests...")
        
        # Test difficulty analyzer
        self.test_difficulty_analyzer()
        
        # Test adaptive quiz system
        self.test_adaptive_quiz_system()
        
        # Test enhanced quiz types
        self.test_enhanced_quiz_types()
        
        # Test mastery-based progression
        self.test_mastery_progression()
        
        # Test intelligent word selection
        self.test_intelligent_word_selection()
        
        # Test enhanced quiz system integration
        self.test_enhanced_quiz_integration()
        
        # Print results
        self.print_test_results()
        
        # Cleanup
        self.cleanup_test_data()
    
    def test_difficulty_analyzer(self):
        """Test word difficulty analysis functionality"""
        try:
            logger.info("Testing difficulty analyzer...")
            
            difficulty_analyzer = DifficultyAnalyzer(self.vocabulary_manager)
            
            # Test individual word analysis
            test_word = {
                'german': 'Schwierigkeitsgrad',
                'english': 'Difficulty level',
                'pronunciation': '/ˈʃviːʁɪçkaɪtsˌɡʁaːt/',
                'category': 'academic',
                'level': 'B2'
            }
            
            analysis = difficulty_analyzer.analyze_word_difficulty(test_word)
            
            # Verify analysis structure
            required_fields = ['word', 'overall_difficulty', 'difficulty_level', 'factors']
            analysis_complete = all(field in analysis for field in required_fields)
            
            # Test difficulty distribution
            distribution = difficulty_analyzer.analyze_vocabulary_difficulty_distribution()
            distribution_valid = 'distribution' in distribution and 'average_difficulty' in distribution
            
            # Test difficulty range selection
            easy_words = difficulty_analyzer.get_words_by_difficulty_range(1.0, 3.0)
            range_selection_works = len(easy_words) > 0
            
            self.test_results.append({
                'test': 'Difficulty Analyzer',
                'passed': analysis_complete and distribution_valid and range_selection_works,
                'details': f"Analysis: {analysis_complete}, Distribution: {distribution_valid}, Range: {range_selection_works}"
            })
            
            logger.info("✅ Difficulty analyzer test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Difficulty Analyzer',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ Difficulty analyzer test failed: {e}")
    
    def test_adaptive_quiz_system(self):
        """Test adaptive quiz system functionality"""
        try:
            logger.info("Testing adaptive quiz system...")
            
            user_progress = UserProgress(self.test_chat_id, self.vocabulary_manager)
            adaptive_quiz = AdaptiveQuizSystem(self.vocabulary_manager, user_progress)
            
            # Add some learned words for testing
            test_words = [
                {'german': 'Hallo', 'english': 'Hello', 'level': 'A1'},
                {'german': 'Danke', 'english': 'Thank you', 'level': 'A1'},
                {'german': 'Schwierig', 'english': 'Difficult', 'level': 'A2'}
            ]
            
            for word in test_words:
                user_progress.add_learned_word(word)
            
            # Test user difficulty level detection
            difficulty_level = adaptive_quiz.get_user_difficulty_level()
            level_detected = difficulty_level in ['beginner', 'intermediate', 'advanced', 'expert']
            
            # Test adaptive quiz types selection
            quiz_types = adaptive_quiz.get_adaptive_quiz_types()
            types_available = len(quiz_types) > 0
            
            # Test word mastery level calculation
            mastery_level = adaptive_quiz.get_word_mastery_level('Hallo')
            mastery_valid = 1 <= mastery_level <= 5
            
            # Test adaptive quiz generation
            quiz_data = adaptive_quiz.generate_adaptive_quiz(word_count=3)
            quiz_generated = quiz_data is not None and len(quiz_data.get('questions', [])) > 0
            
            self.test_results.append({
                'test': 'Adaptive Quiz System',
                'passed': level_detected and types_available and mastery_valid and quiz_generated,
                'details': f"Level: {level_detected}, Types: {types_available}, Mastery: {mastery_valid}, Quiz: {quiz_generated}"
            })
            
            logger.info("✅ Adaptive quiz system test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Adaptive Quiz System',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ Adaptive quiz system test failed: {e}")
    
    def test_enhanced_quiz_types(self):
        """Test enhanced quiz question types"""
        try:
            logger.info("Testing enhanced quiz types...")
            
            user_progress = UserProgress(self.test_chat_id, self.vocabulary_manager)
            adaptive_quiz = AdaptiveQuizSystem(self.vocabulary_manager, user_progress)
            
            test_word = {
                'german': 'Wasser',
                'english': 'Water',
                'example': 'Ich trinke Wasser.',
                'category': 'food_drink',
                'level': 'A1'
            }
            
            # Test different question types
            question_types = [
                'fill_in_blank',
                'sentence_construction',
                'contextual_usage',
                'grammar_focus',
                'audio_recognition',
                'reverse_translation'
            ]
            
            questions_created = 0
            for q_type in question_types:
                try:
                    question = adaptive_quiz.create_adaptive_question(test_word, q_type)
                    if question and 'question' in question:
                        questions_created += 1
                except Exception as e:
                    logger.warning(f"Question type {q_type} failed: {e}")
            
            types_working = questions_created >= len(question_types) * 0.7  # At least 70% working
            
            self.test_results.append({
                'test': 'Enhanced Quiz Types',
                'passed': types_working,
                'details': f"Created {questions_created}/{len(question_types)} question types successfully"
            })
            
            logger.info("✅ Enhanced quiz types test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Enhanced Quiz Types',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ Enhanced quiz types test failed: {e}")
    
    def test_mastery_progression(self):
        """Test mastery-based progression system"""
        try:
            logger.info("Testing mastery progression...")
            
            user_progress = UserProgress(self.test_chat_id, self.vocabulary_manager)
            adaptive_quiz = AdaptiveQuizSystem(self.vocabulary_manager, user_progress)
            
            # Simulate quiz results to test mastery progression
            test_quiz_data = {
                'questions': [
                    {'word_id': 'Hallo', 'type': 'translation', 'difficulty': 1},
                    {'word_id': 'Danke', 'type': 'fill_in_blank', 'difficulty': 2}
                ]
            }
            
            user_answers = [0, 1]  # Simulate correct answers
            
            # Process quiz results
            results = adaptive_quiz.process_adaptive_quiz_results(test_quiz_data, user_answers)
            
            # Check if results contain mastery information
            results_valid = 'score' in results and 'detailed_results' in results
            
            # Test word performance update
            adaptive_quiz.update_word_performance('Hallo', True, 1)
            
            # Test recommendation generation
            recommendations = adaptive_quiz.generate_adaptive_recommendations(results)
            recommendations_generated = len(recommendations) > 0
            
            self.test_results.append({
                'test': 'Mastery Progression',
                'passed': results_valid and recommendations_generated,
                'details': f"Results: {results_valid}, Recommendations: {recommendations_generated}"
            })
            
            logger.info("✅ Mastery progression test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Mastery Progression',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ Mastery progression test failed: {e}")
    
    def test_intelligent_word_selection(self):
        """Test intelligent word selection for quizzes"""
        try:
            logger.info("Testing intelligent word selection...")
            
            user_progress = UserProgress(self.test_chat_id, self.vocabulary_manager)
            adaptive_quiz = AdaptiveQuizSystem(self.vocabulary_manager, user_progress)
            difficulty_analyzer = DifficultyAnalyzer(self.vocabulary_manager)
            
            # Add multiple learned words
            test_words = [
                {'german': 'Hallo', 'english': 'Hello', 'level': 'A1'},
                {'german': 'Danke', 'english': 'Thank you', 'level': 'A1'},
                {'german': 'Wasser', 'english': 'Water', 'level': 'A1'},
                {'german': 'Schwierig', 'english': 'Difficult', 'level': 'A2'},
                {'german': 'Verstehen', 'english': 'Understand', 'level': 'A2'}
            ]
            
            for word in test_words:
                user_progress.add_learned_word(word)
            
            # Test intelligent word selection
            selected_words = adaptive_quiz.select_words_for_quiz(word_count=3)
            selection_works = len(selected_words) > 0
            
            # Test adaptive word selection by difficulty
            adaptive_words = difficulty_analyzer.create_adaptive_word_selection(user_progress, word_count=3)
            adaptive_selection_works = len(adaptive_words) > 0
            
            # Test difficulty recommendation
            recommendation = difficulty_analyzer.recommend_next_difficulty_level(user_progress)
            recommendation_valid = 'recommended_difficulty_range' in recommendation
            
            self.test_results.append({
                'test': 'Intelligent Word Selection',
                'passed': selection_works and adaptive_selection_works and recommendation_valid,
                'details': f"Selection: {selection_works}, Adaptive: {adaptive_selection_works}, Recommendation: {recommendation_valid}"
            })
            
            logger.info("✅ Intelligent word selection test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Intelligent Word Selection',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ Intelligent word selection test failed: {e}")
    
    def test_enhanced_quiz_integration(self):
        """Test enhanced quiz system integration"""
        try:
            logger.info("Testing enhanced quiz system integration...")
            
            user_progress = UserProgress(self.test_chat_id, self.vocabulary_manager)
            enhanced_quiz = EnhancedQuizSystem(self.vocabulary_manager, user_progress)
            
            # Add learned words for testing
            test_words = [
                {'german': 'Hallo', 'english': 'Hello', 'level': 'A1'},
                {'german': 'Danke', 'english': 'Thank you', 'level': 'A1'},
                {'german': 'Wasser', 'english': 'Water', 'level': 'A1'}
            ]
            
            for word in test_words:
                user_progress.add_learned_word(word)
            
            # Test enhanced quiz detection
            should_send = enhanced_quiz.should_send_enhanced_quiz()
            detection_works = isinstance(should_send, bool)
            
            # Test different quiz types
            quiz_types = ['adaptive', 'mastery_focused', 'difficulty_progressive', 'weak_areas']
            quizzes_generated = 0
            
            for quiz_type in quiz_types:
                try:
                    quiz_data = enhanced_quiz.generate_enhanced_quiz(quiz_type, word_count=2)
                    if quiz_data and quiz_data.get('questions'):
                        quizzes_generated += 1
                except Exception as e:
                    logger.warning(f"Quiz type {quiz_type} failed: {e}")
            
            generation_works = quizzes_generated >= len(quiz_types) * 0.5  # At least 50% working
            
            # Test quiz message formatting
            test_quiz = enhanced_quiz.generate_enhanced_quiz('adaptive', word_count=2)
            if test_quiz:
                message = enhanced_quiz.format_enhanced_quiz_message(test_quiz)
                formatting_works = len(message) > 100  # Reasonable message length
            else:
                formatting_works = False
            
            self.test_results.append({
                'test': 'Enhanced Quiz Integration',
                'passed': detection_works and generation_works and formatting_works,
                'details': f"Detection: {detection_works}, Generation: {generation_works}, Formatting: {formatting_works}"
            })
            
            logger.info("✅ Enhanced quiz integration test completed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Enhanced Quiz Integration',
                'passed': False,
                'details': f"Error: {e}"
            })
            logger.error(f"❌ Enhanced quiz integration test failed: {e}")
    
    def print_test_results(self):
        """Print comprehensive test results"""
        logger.info("\n" + "="*60)
        logger.info("PHASE 2: INTERACTIVE ASSESSMENT SYSTEM TEST RESULTS")
        logger.info("="*60)
        
        passed_tests = 0
        total_tests = len(self.test_results)
        
        for result in self.test_results:
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            logger.info(f"{result['test']}: {status}")
            logger.info(f"   Details: {result['details']}")
            
            if result['passed']:
                passed_tests += 1
        
        logger.info("="*60)
        logger.info(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL PHASE 2 TESTS PASSED! Interactive Assessment System is working correctly.")
        else:
            logger.warning(f"⚠️  {total_tests - passed_tests} tests failed. Check implementation.")
        
        logger.info("="*60)

def main():
    """Main function to run Phase 2 tests"""
    try:
        test_suite = Phase2TestSuite()
        test_suite.run_all_tests()
        return True
        
    except Exception as e:
        logger.error(f"Error running Phase 2 tests: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
