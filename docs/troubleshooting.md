# Troubleshooting Guide

## 🚨 Common Issues & Solutions

### Bot Not Responding

#### Problem: Bot doesn't reply to messages
**Possible Causes:**
- ❌ Invalid BOT_TOKEN
- ❌ Bot is frozen/suspended
- ❌ Network connectivity issues
- ❌ Server is down

**Solutions:**
```bash
# 1. Check bot token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# 2. Check server health
curl https://your-app.onrender.com/health

# 3. Check Render service status
# Go to Render dashboard → Your service → Logs

# 4. Verify environment variables
echo $BOT_TOKEN
echo $ADMIN_ID
```

#### Problem: Bot responds slowly
**Solutions:**
- Check server resources in Render dashboard
- Monitor response times in logs
- Consider upgrading to paid Render plan
- Optimize database queries

### Deployment Issues

#### Problem: Build fails on Render
**Common Errors:**
```bash
# Error: Module not found
pip install pyTelegramBotAPI flask pytz requests werkzeug

# Error: Environment variable missing
# Set in Render dashboard:
BOT_TOKEN=your_token_here
ADMIN_ID=your_user_id
API_SECRET_KEY=your_secret_key
```

**Solutions:**
1. **Check requirements.txt**
   ```bash
   pyTelegramBotAPI==4.27.0
   flask==3.1.1
   pytz==2025.2
   requests==2.32.4
   werkzeug==3.1.3
   ```

2. **Verify start command**
   ```bash
   python main.py
   ```

3. **Check Python version**
   ```bash
   # In render.yaml
   python-version: "3.11"
   ```

#### Problem: Service crashes after deployment
**Check logs for:**
- Missing environment variables
- Port binding issues
- Database connection errors
- Memory limitations

**Solutions:**
```bash
# 1. Check service logs
tail -f /var/log/app.log

# 2. Verify port configuration
PORT=5000  # Should be set by Render automatically

# 3. Monitor memory usage
# Upgrade to paid plan if needed
```

### API Issues

#### Problem: API returns 401 Unauthorized
**Solution:**
```bash
# Check API key in request
curl -X POST https://your-app.onrender.com/api/checkbalance \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_correct_secret_key",
    "user_id": "123456789"
  }'
```

#### Problem: API returns 500 Internal Server Error
**Debugging steps:**
1. Check server logs
2. Verify request format
3. Test with minimal data
4. Check database connectivity

**Example:**
```bash
# Test health endpoint first
curl https://your-app.onrender.com/health

# Then test API with valid data
curl -X POST https://your-app.onrender.com/api/userinfo \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key",
    "user_id": "123456789"
  }'
```

### Database Issues

#### Problem: Data not saving
**Check:**
- File permissions
- Disk space
- Write errors in logs

**Solutions:**
```python
# Check if save_data() returns True
if save_data():
    print("Data saved successfully")
else:
    print("Failed to save data")

# Check file permissions
ls -la bot_data.json
```

#### Problem: Data corruption
**Recovery steps:**
```bash
# 1. Check backup file
ls -la bot_data_backup.json

# 2. Restore from backup
cp bot_data_backup.json bot_data.json

# 3. Restart application
```

### User Issues

#### Problem: Users can't withdraw money
**Check:**
- Minimum balance (₹10)
- UPI ID format
- Admin processing queue

**Admin actions:**
1. Check withdrawal requests in admin panel
2. Verify user balance
3. Process pending requests
4. Contact user if issues

#### Problem: Referral not working
**Verification:**
```bash
# Check if referral was processed
# User should receive ₹5 bonus
# Referrer should get notification
```

## 🔧 Diagnostic Commands

### Health Check
```bash
# Basic health check
curl https://your-app.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-07-01T15:30:00",
  "bot_status": "running"
}
```

### API Testing
```bash
# Test user info endpoint
curl -X POST https://your-app.onrender.com/api/userinfo \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_secret_key",
    "user_id": "123456789"
  }'

# Test balance check
curl -X POST https://your-app.onrender.com/api/checkbalance \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_secret_key", 
    "user_id": "123456789"
  }'
```

### Log Analysis
```bash
# Check recent logs
tail -n 100 bot.log

# Search for errors
grep "ERROR" bot.log

# Search for specific user
grep "123456789" bot.log

# Check auto-save status
grep "Auto-save" bot.log
```

## ⚡ Performance Optimization

### Server Performance
- Monitor CPU and memory usage
- Optimize database queries
- Use threading effectively
- Implement caching if needed

### Bot Performance
- Reduce API calls to Telegram
- Optimize message handling
- Use webhooks instead of polling
- Implement rate limiting

### Database Performance
- Regular backup cleanup
- Optimize JSON structure
- Consider database migration for large datasets
- Monitor file sizes

## 🛡️ Security Issues

### API Security
- Rotate API keys regularly
- Monitor API usage
- Implement rate limiting
- Log suspicious activities

### Bot Security
- Keep bot token secure
- Monitor admin access
- Regular security audits
- Update dependencies

## 📞 Getting Help

### Log Files to Check
1. **Application logs**: `bot.log`
2. **Render logs**: Render dashboard → Service → Logs
3. **System logs**: Check Render metrics

### Information to Provide
When seeking help, include:
- Error messages (exact text)
- Log snippets (relevant parts)
- Steps to reproduce
- Environment details
- Render service URL

### Contact Channels
- **GitHub Issues**: Report bugs and feature requests
- **Email Support**: For urgent issues
- **Documentation**: Check docs/ folder for detailed guides

## 🔄 Recovery Procedures

### Complete Service Recovery
```bash
# 1. Check service status
curl https://your-app.onrender.com/health

# 2. Restart service (Render dashboard)
# Manual restart from dashboard

# 3. Verify data integrity
# Check if bot_data.json exists and is valid

# 4. Test all functions
# /start command
# Balance check
# Task browsing
# Admin functions
```

### Data Recovery
```bash
# 1. Stop the service
# 2. Backup current data
cp bot_data.json bot_data_manual_backup.json

# 3. Restore from backup
cp bot_data_backup.json bot_data.json

# 4. Restart service
# 5. Verify functionality
```

## 📈 Monitoring & Maintenance

### Regular Checks
- Daily: Service health, error logs
- Weekly: Database size, backup status  
- Monthly: Performance metrics, user analytics

### Automated Monitoring
- Set up Render alerts
- Monitor API response times
- Track user growth
- Monitor resource usage

### Maintenance Tasks
- Regular log cleanup
- Database optimization
- Security updates
- Feature updates based on user feedback
