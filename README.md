# 🇩🇪 German Daily Word Bot - Enhanced Learning System

A comprehensive Telegram bot that provides personalized German language learning with CEFR level progression, spaced repetition, and interactive features. Transform your German vocabulary learning journey!

## ✨ Enhanced Features

### 🎯 **Progressive Difficulty System (CEFR Levels)**

- **Adaptive Learning**: Starts with A1 (beginner) and progresses to B2 (upper-intermediate)
- **Smart Word Selection**: Mixes current level words with strategic review content
- **Automatic Progression**: Levels up based on vocabulary mastery and consistency
- **Personalized Pace**: Adjusts to individual learning speed and preferences

### 📚 **Comprehensive Vocabulary Database (500+ Words)**

- **CEFR Structured**: Words categorized by A1, A2, B1, B2 difficulty levels
- **Rich Metadata**: Each word includes:
  - IPA pronunciation with audio-ready notation
  - Grammatical information (word type, formality, usage)
  - Cultural context and regional notes
  - Related words, synonyms, and word families
  - Frequency rankings for prioritized learning
  - Real-world usage examples with translations

### 🧠 **Intelligent Learning Features**

- **Spaced Repetition**: Scientific review scheduling for optimal retention
- **Progress Tracking**: Detailed statistics on learning journey and achievements
- **Interactive Quizzes**: Multiple quiz types to reinforce vocabulary
- **Daily Streaks**: Gamification to maintain consistent learning habits
- **Weekly Reports**: Comprehensive analytics and personalized recommendations

### 🎓 **Grammar Integration**

- **Daily Grammar Tips**: Contextual grammar lessons alongside vocabulary
- **Word Type Analysis**: Noun genders, verb conjugations, adjective patterns
- **Sentence Structure**: German syntax patterns and common constructions
- **Case System**: Gradual introduction to German cases (Nominativ, Akkusativ, Dativ, Genitiv)

### 🌍 **Cultural Context**

- **Cultural Notes**: When and how to use words appropriately
- **Formality Levels**: Distinction between formal and informal usage
- **Regional Variations**: Austrian, Swiss, and German differences
- **Social Context**: Business vs. casual vs. family usage patterns

### 🧠 **Interactive Learning (Phase 2)**

- **Vocabulary Quizzes**: Multiple-choice questions testing learned words
- **Spaced Repetition Reviews**: Scientific review scheduling for optimal retention
- **Weekly Progress Reports**: Comprehensive analytics and learning insights
- **Achievement System**: Streaks, level-ups, and milestone celebrations
- **Personalized Recommendations**: AI-powered suggestions based on progress

### 📊 **Advanced Analytics**

- **Learning Pace Analysis**: Words per day and consistency tracking
- **Category Balance**: Vocabulary distribution across topics
- **Retention Metrics**: Success rates and review performance
- **Progress Visualization**: Level completion and goal tracking
- **Motivational Insights**: Personalized encouragement and next steps

## 🚀 Quick Start

### 1. Create Your Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save your bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Send a message to your new bot to activate it

### 2. Get Your Chat ID

1. Clone this repository
2. Copy `.env.example` to `.env`
3. Add your bot token to the `.env` file
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python get_chat_id.py`
6. Add the returned chat ID to your `.env` file

### 3. Test the Bot

```bash
# Test the connection
python test_bot.py

# Send a manual lesson
python send_word.py
```

### 4. Set Up Automation

1. Push your code to GitHub (without the `.env` file!)
2. Go to your repository Settings → Secrets and variables → Actions
3. Add these secrets:
   - `BOT_TOKEN`: Your Telegram bot token
   - `CHAT_ID`: Your chat ID
4. The GitHub Action will automatically run daily at 9:00 AM UTC

## 📁 Project Structure

```
germanworddailybot/
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── requirements.txt     # Python dependencies
├── words.json          # German vocabulary database
├── get_chat_id.py      # Script to retrieve your chat ID
├── test_bot.py         # Bot connection test
├── send_word.py        # Main bot application
└── .github/
    └── workflows/
        └── daily_word.yml  # GitHub Actions automation
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with:

```env
# Your bot token from BotFather
BOT_TOKEN=your_bot_token_here

# Your chat ID (use get_chat_id.py to find this)
CHAT_ID=your_chat_id_here

# Number of words to send per day (3-5 recommended)
WORDS_PER_DAY=3
```

### Customizing Word Count

You can send 3-5 words per day by changing the `WORDS_PER_DAY` value in your `.env` file or GitHub secrets.

## 📚 Vocabulary Database

The `words.json` file contains 100+ German words with:

- **Categories**: greetings, politeness, basic, pronouns, numbers, food_drink, home, transport, colors, family, time, weather, adjectives, verbs, animals, objects
- **IPA Pronunciation**: Accurate International Phonetic Alphabet notation
- **Real Examples**: Practical German sentences with translations

### Adding New Words

To add new vocabulary, edit `words.json` following this structure:

```json
{
  "german": "Hallo",
  "english": "Hello",
  "pronunciation": "/ˈhaloː/",
  "example": "Hallo, wie geht es dir?",
  "example_translation": "Hello, how are you?",
  "category": "greetings"
}
```

## 🤖 Enhanced GitHub Actions Automation

The comprehensive learning system runs automatically via GitHub Actions:

### 📅 **Automated Schedule**

- **Daily Lessons**: Every day at 9:00 AM UTC
- **Vocabulary Quizzes**: Tuesday, Thursday, Saturday at 7:00 PM UTC
- **Weekly Reports**: Sunday at 8:00 PM UTC
- **Manual Triggers**: Run any component on-demand from Actions tab

### ⚙️ **Available Actions**

- `daily_lesson`: Send personalized vocabulary lesson
- `quiz`: Interactive vocabulary quiz and spaced repetition
- `weekly_report`: Comprehensive progress analytics
- `all`: Run all components (for testing)

### 🔧 **Features**

- **Smart Scheduling**: Different content types at optimal times
- **Progress Persistence**: User data maintained across runs
- **Comprehensive Logging**: Detailed execution logs and artifacts
- **Error Handling**: Graceful fallbacks and retry mechanisms

### Manual Trigger

1. Go to your repository on GitHub
2. Click the "Actions" tab
3. Select "Daily German Word"
4. Click "Run workflow"

## 🔧 Local Development

### Prerequisites

- Python 3.7+
- pip

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd germanworddailybot

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Then test the bot
python test_bot.py
```

### Testing

```bash
# Test bot connection
python test_bot.py

# Send a test lesson
python send_word.py

# Get your chat ID
python get_chat_id.py
```

## 📝 Example Output

```
🌅 German Words of the Day
📅 Monday, December 16, 2024
📚 Today's vocabulary lesson (3 words)
========================================

1. Hallo
🇺🇸 Hello
🔊 /ˈhaloː/
📝 Hallo, wie geht es dir?
💭 Hello, how are you?

2. Danke
🇺🇸 Thank you
🔊 /ˈdaŋkə/
📝 Danke für deine Hilfe!
💭 Thank you for your help!

3. Wasser
🇺🇸 Water
🔊 /ˈvasɐ/
📝 Ich trinke gerne Wasser.
💭 I like to drink water.

========================================
🎯 Practice Tip: Try using these words in your own sentences today!
🔄 New words tomorrow at the same time.
📖 Keep learning, keep growing! 🌱
```

## 🛠️ Troubleshooting

### Common Issues

1. **"BOT_TOKEN not found"**: Make sure your `.env` file exists and contains the bot token
2. **"CHAT_ID not found"**: Run `get_chat_id.py` to retrieve your chat ID
3. **"No messages found"**: Send a message to your bot first, then run `get_chat_id.py`
4. **GitHub Actions failing**: Check that your repository secrets are set correctly

### Logs

The bot creates a `bot.log` file with detailed execution information. Check this file for debugging.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new vocabulary or improve functionality
4. Test your changes
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Vocabulary sourced from standard German language learning materials
- IPA pronunciations verified against linguistic resources
- Built with the Telegram Bot API

---

**Happy German learning! 🇩🇪📚**
