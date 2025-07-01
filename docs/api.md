# API Documentation

## Authentication

All API endpoints require authentication using the `api_key` parameter.

## Endpoints

### POST /api/checkbalance
Check user balance

**Request:**
```json
{
  "api_key": "your_secret_key",
  "user_id": "123456789"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 123456789,
  "balance": 25.50,
  "timestamp": "2025-07-01 15:30:00"
}
```

### POST /api/addbalance
Add balance to user account

**Request:**
```json
{
  "api_key": "your_secret_key", 
  "user_id": "123456789",
  "amount": 10.0
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 123456789,
  "amount_added": 10.0,
  "new_balance": 35.50,
  "timestamp": "2025-07-01 15:30:00"
}
```

### POST /api/userinfo
Get user information

**Request:**
```json
{
  "api_key": "your_secret_key",
  "user_id": "123456789"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 123456789,
  "balance": 25.50,
  "completed_tasks": 15,
  "referrals": 3,
  "is_banned": false,
  "timestamp": "2025-07-01 15:30:00"
}
```

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-01T15:30:00",
  "bot_status": "running"
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Invalid API key"
}
```

### 400 Bad Request
```json
{
  "error": "user_id and amount required"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Example Usage

### cURL Examples

```bash
# Check user balance
curl -X POST https://your-app.onrender.com/api/checkbalance \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_secret_key",
    "user_id": "123456789"
  }'

# Add user balance
curl -X POST https://your-app.onrender.com/api/addbalance \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_secret_key",
    "user_id": "123456789",
    "amount": 10.0
  }'

# Get user info
curl -X POST https://your-app.onrender.com/api/userinfo \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_secret_key",
    "user_id": "123456789"
  }'

# Health check
curl https://your-app.onrender.com/health
```

### Python Examples

```python
import requests

# API configuration
BASE_URL = "https://your-app.onrender.com"
API_KEY = "your_secret_key"

# Check balance
def check_balance(user_id):
    response = requests.post(f"{BASE_URL}/api/checkbalance", json={
        "api_key": API_KEY,
        "user_id": str(user_id)
    })
    return response.json()

# Add balance
def add_balance(user_id, amount):
    response = requests.post(f"{BASE_URL}/api/addbalance", json={
        "api_key": API_KEY,
        "user_id": str(user_id),
        "amount": float(amount)
    })
    return response.json()

# Get user info
def get_user_info(user_id):
    response = requests.post(f"{BASE_URL}/api/userinfo", json={
        "api_key": API_KEY,
        "user_id": str(user_id)
    })
    return response.json()
```

## Rate Limits

- 100 requests per minute per API key
- 1000 requests per hour per API key

## Security

- Always use HTTPS for API requests
- Keep your API key secure and don't share it
- Validate all user inputs before sending to API
- Monitor API usage for unusual activity
