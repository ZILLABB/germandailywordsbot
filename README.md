# 🇩🇪 German Daily Word Bot

An advanced AI-powered Telegram bot for learning German with enterprise-level features including adaptive quizzes, comprehensive analytics, and intelligent progress tracking.

## 🌟 Features

### 📚 **Core Learning Features**

- **Daily German Lessons**: 3-5 words with pronunciation, examples, and cultural context
- **Progressive Difficulty**: CEFR levels A1 → A2 → B1 → B2 with automatic advancement
- **Spaced Repetition**: Intelligent review scheduling for optimal retention

### 🧠 **Advanced Quiz System (Phase 2)**

- **6 Question Types**: Fill-in-blank, sentence construction, contextual usage, grammar focus, audio recognition, reverse translation
- **Adaptive Difficulty**: Questions automatically adjust to user skill level
- **4 Quiz Modes**: Adaptive, mastery-focused, progressive difficulty, weak areas
- **Intelligent Word Selection**: AI prioritizes words based on mastery and performance

### 🔥 **Advanced Streak System (Phase 1)**

- **9 Milestone Levels**: From 7-day "Week Warrior" to 1000-day "Millennium Master"
- **Streak Protection**: Grace periods and streak freezes to prevent frustration
- **Achievement System**: Unlock rewards and bonuses for consistency

### 📊 **Comprehensive Analytics (Phase 1)**

- **Learning Insights**: Study patterns, strengths/weaknesses, retention rates
- **Performance Tracking**: Quiz scores, category breakdown, progress trends
- **Predictive Analytics**: Engagement risk assessment, 30-day projections
- **Weekly Reports**: Automated comprehensive learning summaries

### 👥 **Multi-User Support**

- **Unlimited Users**: Independent progress tracking for each user
- **Real-Time Commands**: 8 interactive commands with instant responses
- **User Management**: Automatic registration and onboarding

### 🌐 **Phase 3: Multi-Platform Support (Coming Soon)**

- **WhatsApp Integration**: Reach 2+ billion WhatsApp users globally
- **Voice Pronunciation**: Audio messages for perfect German pronunciation
- **Visual Vocabulary**: Images and multimedia for enhanced learning
- **Group Learning**: WhatsApp groups for collaborative practice
- **Cross-Platform Sync**: Seamless progress across Telegram and WhatsApp

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Telegram Bot Token (from @BotFather)
- Your Telegram Chat ID

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/ZILLABB/germandailywordsbot.git
   cd germandailywordsbot
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   # Create .env file
   cp .env.example .env

   # Edit .env with your credentials
   BOT_TOKEN=your_telegram_bot_token_here
   CHAT_ID=your_telegram_chat_id_here
   WORDS_PER_DAY=3
   ```

4. **Test the bot**

   ```bash
   python test_bot_functionality.py
   ```

5. **Start the bot**
   ```bash
   python run_telegram_bot.py
   ```

## 📁 Project Structure

```
germanworddailybot/
├── 📚 Core Bot Files
│   ├── multi_user_bot.py              # Daily lesson delivery system
│   ├── vocabulary_manager.py          # Word database and selection
│   ├── user_progress.py              # Progress tracking and analytics
│   └── run_telegram_bot.py           # Real-time bot listener
│
├── 🧠 Phase 2: Interactive Assessment
│   ├── adaptive_quiz_system.py       # Adaptive quiz engine
│   ├── difficulty_analyzer.py        # Word difficulty analysis
│   ├── enhanced_quiz_system.py       # Integrated quiz management
│   └── quiz_system.py               # Basic quiz functionality
│
├── 📊 Phase 1: Advanced Analytics
│   ├── streak_manager.py             # Advanced streak tracking
│   ├── learning_analytics.py         # Comprehensive analytics
│   ├── analytics_dashboard.py        # Report generation
│   └── send_weekly_analytics.py      # Automated reports
│
├── 👥 Multi-User Support
│   ├── multi_user_setup.py           # User management system
│   ├── telegram_bot_handler.py       # Command processing
│   ├── send_quiz.py                  # Individual quiz delivery
│   └── multi_user_quiz.py           # Multi-user quiz system
│
├── 🧪 Testing & Demo
│   ├── test_analytics.py             # Phase 1 feature tests
│   ├── test_phase2_features.py       # Phase 2 feature tests
│   ├── test_bot_functionality.py     # Complete system test
│   ├── demo_analytics.py             # Phase 1 demo
│   └── demo_phase2_features.py       # Phase 2 demo
│
├── 🌐 Deployment
│   ├── webhook_server.py             # Flask webhook server
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment template
│   └── .gitignore                    # Git exclusions
│
├── 🚀 Phase 3: Multi-Platform (Coming Soon)
│   ├── whatsapp_bot_handler.py       # WhatsApp message processing
│   ├── whatsapp_business_api.py      # Official API integration
│   ├── multi_platform_manager.py    # Cross-platform coordination
│   ├── voice_message_handler.py     # Audio processing
│   └── media_content_manager.py     # Multimedia handling
│
└── 📖 Documentation
    ├── README.md                      # This file
    ├── DEPLOYMENT_GUIDE.md           # Complete deployment guide
    ├── ADVANCED_ANALYTICS_FEATURES.md # Phase 1 documentation
    ├── PHASE2_INTERACTIVE_ASSESSMENT.md # Phase 2 documentation
    └── PHASE3_MULTI_PLATFORM_ANNOUNCEMENT.md # Phase 3 roadmap
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

## 🎯 Roadmap

### Phase 3: Multi-Platform Support 🚀 (In Development)

- **WhatsApp Business API Integration**: Reach 2+ billion WhatsApp users globally
- **Voice Pronunciation Practice**: Audio messages for perfect German pronunciation
- **Visual Vocabulary Learning**: Images and multimedia for enhanced comprehension
- **Group Learning Features**: WhatsApp groups for collaborative practice
- **Cross-Platform Progress Sync**: Seamless learning across Telegram and WhatsApp
- **Enhanced Multimedia Content**: Voice notes, images, and interactive media
- **Social Learning Features**: Community challenges and leaderboards
- **Advanced Voice Recognition**: AI-powered pronunciation feedback

### Future Phases (Planned)

- **Mobile App**: Native iOS and Android applications
- **Web Dashboard**: Browser-based learning interface
- **AI Conversation Partner**: Practice conversations with AI
- **Personalized Learning Paths**: Custom curricula based on goals
- **Integration with Language Schools**: Professional education partnerships

## 🙏 Acknowledgments

- Vocabulary sourced from standard German language learning materials
- IPA pronunciations verified against linguistic resources
- Built with the Telegram Bot API and WhatsApp Business API
- Community feedback and contributions from German learners worldwide

---

**🇩🇪 Viel Erfolg beim Deutschlernen! (Good luck learning German!) 🚀**
