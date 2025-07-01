# Telegram Bot Deployment Guide - Render Platform

এই গাইড আপনাকে আপনার Telegram money bot টি Render প্ল্যাটফর্মে deploy করতে সাহায্য করবে।

## 📋 প্রয়োজনীয় জিনিসপত্র

### 1. Telegram Bot তৈরি করুন
```
1. Telegram এ @BotFather কে message করুন
2. /newbot command পাঠান
3. Bot এর নাম দিন (উদাহরণ: My Money Bot)
4. Bot এর username দিন (উদাহরণ: my_money_bot)
5. Bot token সেভ করুন (যেমন: 123456789:ABCdefGHI...)
```

### 2. Admin ID খুঁজে নিন
```
1. @userinfobot কে message করুন Telegram এ
2. আপনার user ID নোট করুন (যেমন: 123456789)
```

## 🚀 Render এ Deployment

### ধাপ 1: Render Account তৈরি করুন
- https://render.com এ যান
- GitHub দিয়ে sign up করুন
- Free plan নির্বাচন করুন

### ধাপ 2: GitHub Repository তৈরি করুন
```bash
1. GitHub এ নতুন repository তৈরি করুন
2. সব কোড ফাইল upload করুন:
   - main.py
   - render.yaml
   - Dockerfile
   - start.sh
   - health_check.py
   - README.md
   - .env.example
   - .gitignore
```

### ধাপ 3: Render এ Web Service তৈরি করুন

#### Option A: render.yaml ব্যবহার করে (সহজ)
1. Render dashboard এ "New" ক্লিক করুন
2. "Blueprint" নির্বাচন করুন  
3. GitHub repository connect করুন
4. render.yaml ফাইল automatically detect হবে

#### Option B: Manual setup
1. "New Web Service" ক্লিক করুন
2. GitHub repository connect করুন
3. নিম্নলিখিত settings:
   ```
   Name: telegram-money-bot
   Environment: Python
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   ```

### ধাপ 4: Environment Variables সেট করুন

Render dashboard এ Environment variables যোগ করুন:

```
BOT_TOKEN = your_bot_token_from_botfather
ADMIN_ID = your_telegram_user_id  
API_SECRET_KEY = your_secure_random_key_here
PORT = 5000
ENVIRONMENT = production
```

**উদাহরণ:**
```
BOT_TOKEN = 7429740172:AAEUV6A-YmDSzmL0b_0tnCCQ6SbJBEFDXbg
ADMIN_ID = 7929115529
API_SECRET_KEY = mySecretKey123456789
PORT = 5000
ENVIRONMENT = production
```

### ধাপ 5: Deploy করুন
1. "Create Web Service" ক্লিক করুন
2. Deployment process শুরু হবে
3. 5-10 মিনিট অপেক্ষা করুন

## ✅ যাচাই করুন

### 1. Health Check
আপনার deployed URL এ যান:
```
https://your-app-name.onrender.com/health
```

Response দেখা উচিত:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-01T15:46:22",
  "bot_status": "running"
}
```

### 2. Bot Test করুন
1. Telegram এ আপনার bot কে message করুন
2. /start command পাঠান
3. Menu options দেখা উচিত

### 3. API Test করুন
```bash
curl -X POST https://your-app-name.onrender.com/api/userinfo \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_secret_key",
    "user_id": "123456789"
  }'
```

## 🔧 Troubleshooting

### সমস্যা 1: Bot start হচ্ছে না
```
✅ BOT_TOKEN সঠিক কিনা চেক করুন
✅ ADMIN_ID সঠিক কিনা চেক করুন  
✅ Environment variables সেট করা আছে কিনা দেখুন
```

### সমস্যা 2: Application crash হচ্ছে
```
✅ Render logs চেক করুন
✅ PORT environment variable 5000 সেট করুন
✅ start.sh ফাইল executable কিনা চেক করুন
```

### সমস্যা 3: API কাজ করছে না
```
✅ API_SECRET_KEY সঠিক কিনা চেক করুন
✅ Health endpoint /health এ access করে দেখুন
✅ Content-Type: application/json header যোগ করুন
```

## 📊 Features যাচাই করুন

আপনার bot এ নিম্নলিখিত features কাজ করা উচিত:

### User Features:
- ✅ /start command
- ✅ Balance check  
- ✅ Task browsing
- ✅ Referral system
- ✅ Withdrawal requests
- ✅ Support system

### Admin Features:
- ✅ /admin command
- ✅ Task management
- ✅ User balance management
- ✅ Withdrawal processing
- ✅ User statistics
- ✅ Bot controls

### API Features:
- ✅ Add balance endpoint
- ✅ Check balance endpoint  
- ✅ User info endpoint
- ✅ Health check endpoint

## 🔐 Security Tips

1. **API Key:** আপনার API_SECRET_KEY গোপন রাখুন
2. **Bot Token:** BOT_TOKEN কখনো share করবেন না
3. **Admin Access:** ADMIN_ID শুধুমাত্র আপনার ID দিন
4. **Environment Variables:** Production এ সব values সঠিক রাখুন

## 📞 Support

যদি কোন সমস্যা হয়:
1. Render logs চেক করুন
2. Health endpoint test করুন  
3. Environment variables verify করুন
4. GitHub repository এ কোড সঠিক আছে কিনা দেখুন

## 🎉 Congratulations!

আপনার Telegram money bot এখন সম্পূর্ণভাবে deployed এবং production ready! 

Users এখন:
- Tasks complete করে money earn করতে পারবে
- Referral link share করতে পারবে
- UPI তে withdraw করতে পারবে
- Admin panel ব্যবহার করতে পারবে

App URL: `https://your-app-name.onrender.com`
Bot Link: `https://t.me/your_bot_username`
