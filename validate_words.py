#!/usr/bin/env python3
"""
Validate the words.json file structure and content
"""

import json
import sys

def validate_words():
    """Validate the words.json file"""
    try:
        with open('words.json', 'r', encoding='utf-8') as f:
            words = json.load(f)
        
        print(f"✅ Successfully loaded {len(words)} words from words.json")
        
        # Check structure
        required_fields = ['german', 'english', 'pronunciation', 'example', 'example_translation', 'category']
        
        for i, word in enumerate(words):
            for field in required_fields:
                if field not in word:
                    print(f"❌ Word {i+1} missing field: {field}")
                    return False
                if not word[field] or not isinstance(word[field], str):
                    print(f"❌ Word {i+1} has invalid {field}: {word[field]}")
                    return False
        
        # Count categories
        categories = {}
        for word in words:
            cat = word['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n📊 Word distribution by category:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} words")
        
        print(f"\n🎯 Total categories: {len(categories)}")
        print(f"🎯 Average words per category: {len(words) / len(categories):.1f}")
        
        # Check for enough words for daily lessons
        days_of_content = len(words) // 3  # Assuming 3 words per day
        print(f"\n📅 Content available for approximately {days_of_content} days")
        
        if len(words) >= 365:
            print("✅ Enough words for a full year!")
        elif len(words) >= 100:
            print("✅ Good vocabulary base!")
        else:
            print("⚠️  Consider adding more words for better variety")
        
        return True
        
    except FileNotFoundError:
        print("❌ words.json file not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in words.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating words: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Validating German vocabulary database...")
    print("=" * 50)
    
    success = validate_words()
    
    if success:
        print("\n🎉 Validation successful! Your vocabulary database is ready.")
    else:
        print("\n💥 Validation failed. Please fix the issues above.")
        sys.exit(1)
