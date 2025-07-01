# 💰 Telegram Money Bot - Task Based Earning Platform

A feature-rich Telegram bot for task-based earning with Flask API integration, ready for deployment on Render platform.

![Bot Demo](assets/bot-demo.png)

## ⚡ Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. **Create Telegram Bot:**
   - Message [@BotFather](https://t.me/BotFather) → `/newbot`
   - Save your bot token

2. **Get Admin ID:**
   - Message [@userinfobot](https://t.me/userinfobot)
   - Save your user ID

3. **Deploy:**
   - Click "Deploy to Render" button above
   - Set environment variables:
     ```
     BOT_TOKEN=your_bot_token_here
     ADMIN_ID=your_user_id_here
     API_SECRET_KEY=your_secret_key
     ```

## 🌟 Features

### 💰 For Users
- **Task System**: Complete tasks and earn money
- **Referral Program**: ₹5 per successful referral  
- **UPI Withdrawal**: Minimum ₹10 withdrawal
- **Real-time Balance**: Track earnings instantly
- **Multiple Categories**: Ads, Apps, Promotions

### ⚙️ For Admins
- **Admin Panel**: Complete management interface
- **Task Management**: Add/remove tasks dynamically
- **User Analytics**: Detailed user statistics
- **Withdrawal Processing**: Handle user payments
- **Security Controls**: Freeze/unfreeze operations

### 🔧 Technical
- **Flask API**: RESTful endpoints for integration
- **Auto-save**: Data persistence every 30 seconds
- **Health Monitoring**: Built-in health checks
- **Dynamic Emojis**: 24-hour emoji rotation
- **JSON Storage**: Simple file-based storage

## 🚀 Live Demo

- **Bot**: [@your_bot_username](https://t.me/your_bot_username)
- **API**: `https://your-app.onrender.com`
- **Health**: `https://your-app.onrender.com/health`

## 📱 Screenshots

| User Interface | Admin Panel | API Response |
|---|---|---|
| ![User](assets/user-interface.png) | ![Admin](assets/admin-panel.png) | ![API](assets/api-response.png) |

## 🛠️ Local Development

```bash
# Clone repository
git clone https://github.com/your-username/telegram-money-bot.git
cd telegram-money-bot

# Install dependencies
pip install pyTelegramBotAPI flask pytz requests werkzeug

# Set environment variables
export BOT_TOKEN="your_bot_token"
export ADMIN_ID="your_user_id"
export API_SECRET_KEY="your_secret_key"

# Run application
python main.py
