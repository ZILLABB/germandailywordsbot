#!/usr/bin/env python3
"""
Webhook Server for Telegram Bot (Alternative to Polling)
Use this for production deployment with a web server
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Import bot handler
try:
    from telegram_bot_handler import TelegramBotHandler
    BOT_HANDLER_AVAILABLE = True
except ImportError as e:
    print(f"❌ Bot handler not available: {e}")
    BOT_HANDLER_AVAILABLE = False

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize bot handler
if BOT_HANDLER_AVAILABLE:
    bot_handler = TelegramBotHandler()
else:
    bot_handler = None

@app.route('/', methods=['GET'])
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'German Daily Word Bot Webhook Server',
        'bot_available': BOT_HANDLER_AVAILABLE
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for Telegram updates"""
    try:
        if not bot_handler:
            return jsonify({'error': 'Bot handler not available'}), 500
        
        # Get update data
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({'error': 'No data received'}), 400
        
        # Process the update
        bot_handler.process_update(update_data)
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Set webhook URL for the bot"""
    try:
        import requests
        
        bot_token = os.getenv('BOT_TOKEN')
        webhook_url = request.json.get('webhook_url')
        
        if not bot_token or not webhook_url:
            return jsonify({'error': 'Missing bot_token or webhook_url'}), 400
        
        # Set webhook
        api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        data = {'url': webhook_url}
        
        response = requests.post(api_url, data=data)
        
        if response.status_code == 200:
            return jsonify({'status': 'Webhook set successfully'})
        else:
            return jsonify({'error': response.text}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not BOT_HANDLER_AVAILABLE:
        print("❌ Cannot start webhook server: Bot handler not available")
        exit(1)
    
    print("🌐 Starting Webhook Server for German Daily Word Bot")
    print("📡 Webhook endpoint: /webhook")
    print("🔧 Health check: /")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=False
    )
