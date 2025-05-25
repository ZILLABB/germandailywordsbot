# 🚀 Setup Instructions for German Daily Word Bot

## Step 1: Get Your Chat ID

Since you already have your bot token, you need to get your chat ID. Here's how:

### Method 1: Using the Web Browser (Easiest)

1. **Send a message to your bot first**: Go to https://t.me/Germandailywordbot and send any message (like "Hello")

2. **Get your chat ID**: Open this URL in your browser (replace with your bot token):
   ```
   https://api.telegram.org/bot8034239690:AAFDuvCGSax5PcPOMT5b-F7guXf3KxWsOR4/getUpdates
   ```

3. **Find your chat ID**: Look for the `"chat":{"id":` field in the response. The number after `"id":` is your chat ID.

### Method 2: Using Python (if you have Python installed)

1. **Install dependencies**:
   ```bash
   pip install requests python-dotenv
   ```

2. **Run the chat ID script**:
   ```bash
   python get_chat_id.py
   ```

## Step 2: Update Your .env File

1. Open the `.env` file in this directory
2. Replace `your_chat_id_here` with the chat ID you found
3. Your `.env` file should look like:
   ```
   BOT_TOKEN=8034239690:AAFDuvCGSax5PcPOMT5b-F7guXf3KxWsOR4
   CHAT_ID=123456789
   WORDS_PER_DAY=3
   ```

## Step 3: Test the Bot

Run the test script to make sure everything works:
```bash
python test_bot.py
```

## Step 4: Send Your First Lesson

Test the daily word functionality:
```bash
python send_word.py
```

## Step 5: Set Up GitHub Automation

1. **Create a GitHub repository** and push this code
2. **Add secrets** in your repository settings:
   - Go to Settings → Secrets and variables → Actions
   - Add `BOT_TOKEN`: `8034239690:AAFDuvCGSax5PcPOMT5b-F7guXf3KxWsOR4`
   - Add `CHAT_ID`: (your chat ID from step 1)

3. **The bot will automatically run daily at 9:00 AM UTC**

## Troubleshooting

- **"No messages found"**: Make sure you sent a message to your bot first
- **"BOT_TOKEN not found"**: Check that your `.env` file exists and has the correct format
- **Python not found**: Install Python from https://python.org

## Next Steps

- Customize the number of words per day (3-5 recommended)
- Add more vocabulary to `words.json`
- Adjust the schedule in `.github/workflows/daily_word.yml`

**You're all set! 🎉**
