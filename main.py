import telebot
from telebot import types
import re
import time
import uuid
import threading
import json
import os
from datetime import datetime, timedelta
import pytz
import logging
import random
from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

# Configure logging for production
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ✅ BOT CONFIG - Use environment variables for security
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# Development/Test mode fallback
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'

if not BOT_TOKEN:
    if DEVELOPMENT_MODE:
        logger.warning("Running in development mode without real bot token")
        BOT_TOKEN = "7429740172:AAEUV6A-YmDSzmL0b_0tnCCQ6SbJBEFDXbg"  # Valid format for testing
        ADMIN_ID = 7929115529
    else:
        logger.error("BOT_TOKEN environment variable is required!")
        raise ValueError("BOT_TOKEN environment variable is required!")

if ADMIN_ID == 0:
    if DEVELOPMENT_MODE:
        ADMIN_ID = 123456789
    else:
        logger.error("ADMIN_ID environment variable is required!")
        raise ValueError("ADMIN_ID environment variable is required!")

# ✅ FLASK API CONFIG
app = Flask(__name__)
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'your_secret_api_key_here_change_this')
API_ENDPOINTS = {
    'add_balance': '/api/addbalance',
    'check_balance': '/api/checkbalance',
    'user_info': '/api/userinfo'
}

# Health check endpoint for Render
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_status': 'running' if BOT_USERNAME else 'initializing'
    }), 200

@app.route('/')
def home():
    return jsonify({
        'message': 'Telegram Bot API Server',
        'status': 'running',
        'endpoints': list(API_ENDPOINTS.values())
    })

try:
    bot = telebot.TeleBot(BOT_TOKEN)
    logger.info("Bot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}")
    raise

# ✅ BOT USERNAME CACHE
BOT_USERNAME = None

def get_bot_username():
    """Get and cache bot username with retry mechanism"""
    global BOT_USERNAME
    if BOT_USERNAME is None:
        try:
            bot_info = bot.get_me()
            BOT_USERNAME = bot_info.username or "TelegramBot"
            logger.info(f"Bot username retrieved: {BOT_USERNAME}")
        except Exception as e:
            logger.error(f"Error getting bot username: {e}")
            BOT_USERNAME = "TelegramBot"
    return BOT_USERNAME

def get_local_time():
    """Get local time in Indian Standard Time (UTC+5:30)"""
    indian_tz = pytz.timezone('Asia/Kolkata')
    local_time = datetime.now(indian_tz)
    return local_time.strftime("%Y-%m-%d %H:%M:%S")

# ✅ DATA PERSISTENCE
DATA_FILE = "bot_data.json"
BACKUP_FILE = "bot_data_backup.json"

def load_data():
    """Load data from file with backup recovery"""
    default_data = {
        'user_balances': {},
        'worked_users': {},
        'pending_tasks': {},
        'referral_data': {},
        'banned_users': [],
        'completed_tasks': {},
        'task_sections': {
            'watch_ads': [],
            'app_downloads': [],
            'promotional': []
        },
        'client_tasks': {},
        'client_referrals': {},
        'client_id_counter': 1,
        'withdrawal_requests': {},
        'task_tracking': {}
    }

    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure all required keys exist
                for key in default_data:
                    if key not in data:
                        data[key] = default_data[key]
                logger.info("Data loaded successfully from main file")
                return data
        elif os.path.exists(BACKUP_FILE):
            logger.info("Loading from backup file...")
            with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure all required keys exist
                for key in default_data:
                    if key not in data:
                        data[key] = default_data[key]
                logger.info("Data loaded successfully from backup")
                return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        if os.path.exists(BACKUP_FILE):
            try:
                with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key in default_data:
                        if key not in data:
                            data[key] = default_data[key]
                    logger.info("Successfully loaded from backup after JSON error")
                    return data
            except Exception as backup_error:
                logger.error(f"Backup loading failed: {backup_error}")
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        if os.path.exists(BACKUP_FILE):
            try:
                with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key in default_data:
                        if key not in data:
                            data[key] = default_data[key]
                    logger.info("Successfully loaded from backup")
                    return data
            except Exception as backup_error:
                logger.error(f"Backup loading failed: {backup_error}")

    logger.warning("Using default data structure")
    return default_data

def save_data():
    """Save data to file with enhanced backup and verification"""
    try:
        # Create backup before saving
        if os.path.exists(DATA_FILE):
            import shutil
            try:
                shutil.copy2(DATA_FILE, BACKUP_FILE)
            except Exception as backup_error:
                logger.warning(f"Failed to create backup: {backup_error}")

        data = {
            'user_balances': user_balances,
            'worked_users': worked_users,
            'pending_tasks': pending_tasks,
            'referral_data': referral_data,
            'banned_users': list(banned_users),
            'completed_tasks': {str(k): list(v) if isinstance(v, set) else v for k, v in completed_tasks.items()},
            'task_sections': task_sections,
            'client_tasks': client_tasks,
            'client_referrals': client_referrals,
            'client_id_counter': client_id_counter,
            'withdrawal_requests': withdrawal_requests,
            'task_tracking': task_tracking if 'task_tracking' in globals() else {},
            'save_timestamp': get_local_time(),
            'data_integrity_check': len(user_balances)
        }

        # Atomic write with verification
        temp_file = DATA_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Verify written data
        with open(temp_file, 'r', encoding='utf-8') as f:
            verification_data = json.load(f)
            if verification_data.get('data_integrity_check') != len(user_balances):
                raise Exception("Data integrity check failed")

        os.replace(temp_file, DATA_FILE)
        logger.debug("Data saved successfully")
        return True

    except Exception as e:
        logger.error(f"Error saving data: {e}")
        # Clean up temp file if it exists
        temp_file = DATA_FILE + '.tmp'
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

        # Try to restore from backup if save fails
        if os.path.exists(BACKUP_FILE):
            try:
                import shutil
                shutil.copy2(BACKUP_FILE, DATA_FILE)
                logger.info("Restored from backup after save failure")
            except Exception as restore_error:
                logger.error(f"Failed to restore from backup: {restore_error}")
        return False

# Load initial data
try:
    initial_data = load_data()

    # Safe data conversion with error handling
    user_balances = {}
    for k, v in initial_data.get('user_balances', {}).items():
        try:
            user_balances[int(k)] = float(v)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid user balance data: {k}={v}, error: {e}")

    worked_users = initial_data.get('worked_users', {})
    pending_tasks = initial_data.get('pending_tasks', {})

    referral_data = {}
    for k, v in initial_data.get('referral_data', {}).items():
        try:
            referral_data[int(k)] = int(v)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid referral data: {k}={v}, error: {e}")

    banned_users = set()
    for x in initial_data.get('banned_users', []):
        try:
            banned_users.add(int(x))
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid banned user ID: {x}, error: {e}")

    completed_tasks = {}
    for k, v in initial_data.get('completed_tasks', {}).items():
        try:
            completed_tasks[int(k)] = set(v) if isinstance(v, list) else v
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid completed task data: {k}={v}, error: {e}")

    task_sections = initial_data.get('task_sections', {
        'watch_ads': [],
        'app_downloads': [],
        'promotional': []
    })

    # Ensure all required sections exist
    for section in ['watch_ads', 'app_downloads', 'promotional']:
        if section not in task_sections:
            task_sections[section] = []

    client_tasks = initial_data.get('client_tasks', {})
    client_referrals = initial_data.get('client_referrals', {})
    client_id_counter = initial_data.get('client_id_counter', 1)
    withdrawal_requests = initial_data.get('withdrawal_requests', {})
    task_tracking = initial_data.get('task_tracking', {})

    logger.info("Data initialization completed successfully")

except Exception as e:
    logger.error(f"Critical error during data initialization: {e}")
    # Initialize with defaults
    user_balances = {}
    worked_users = {}
    pending_tasks = {}
    referral_data = {}
    banned_users = set()
    completed_tasks = {}
    task_sections = {'watch_ads': [], 'app_downloads': [], 'promotional': []}
    client_tasks = {}
    client_referrals = {}
    client_id_counter = 1
    withdrawal_requests = {}
    task_tracking = {}

# Remove admin ID from banned users if accidentally banned
banned_users.discard(ADMIN_ID)

# ✅ Runtime variables (not saved to disk)
awaiting_withdraw = {}
awaiting_message = {}
awaiting_task_add = {}
awaiting_support_message = {}
awaiting_promotion_message = {}
awaiting_client_data = {}
awaiting_task_remove = {}
awaiting_notice = {}
awaiting_referral_reset = {}

# ✅ SECURITY SYSTEM - Bot Freeze/Unfreeze Feature
bot_frozen = False
freeze_timestamp = None
awaiting_unlock_code = {}

# Security codes (keep these secret!)
FREEZE_CODE = "/stop2833"
UNFREEZE_CODE = "/connect2833"

# Auto-save with improved error handling and thread safety
def auto_save():
    save_count = 0
    while True:
        try:
            time.sleep(30)  # Increased to 30 seconds to reduce I/O
            if save_data():
                save_count += 1
                logger.info(f"✅ Auto-save completed (#{save_count})")
            else:
                logger.error("❌ Auto-save failed")
        except KeyboardInterrupt:
            logger.info("Auto-save thread interrupted")
            break
        except Exception as e:
            logger.error(f"❌ Auto-save error: {e}")

# Emoji rotation function
def emoji_rotation_monitor():
    """Monitor and update emojis every 24 hours"""
    while True:
        try:
            time.sleep(3600)  # Check every hour
            get_current_emoji('task')  # This will trigger rotation if 24 hours have passed
        except KeyboardInterrupt:
            logger.info("Emoji rotation thread interrupted")
            break
        except Exception as e:
            logger.error(f"❌ Emoji rotation error: {e}")

# Start auto-save thread
try:
    save_thread = threading.Thread(target=auto_save, daemon=True)
    save_thread.start()
    logger.info("Auto-save thread started")
except Exception as e:
    logger.error(f"Failed to start auto-save thread: {e}")

# Start emoji rotation thread  
try:
    emoji_thread = threading.Thread(target=emoji_rotation_monitor, daemon=True)
    emoji_thread.start()
    logger.info("🎨 Emoji rotation thread started - 24-hour auto-update active")
except Exception as e:
    logger.error(f"Failed to start emoji rotation thread: {e}")

# Thread lock for data operations
data_lock = threading.Lock()

# ✅ DYNAMIC EMOJI SYSTEM - Changes every 24 hours
EMOJI_SETS = {
    'task': ['🎯', '⚡', '🚀', '💎', '🔥', '⭐', '🎪', '🎭', '🎨', '🎲'],
    'balance': ['💎', '💰', '💳', '🏆', '💸', '💵', '🤑', '💹', '💲', '🎁'],
    'submit': ['🚀', '📸', '✨', '🎯', '💫', '⚡', '🔥', '🌟', '💎', '🎪'],
    'withdraw': ['💸', '💳', '🏦', '💰', '🤑', '💵', '💲', '🏧', '💹', '🎁'],
    'referral': ['👥', '🤝', '🔗', '💪', '🌟', '👑', '🎯', '💎', '🚀', '⭐'],
    'admin': ['⚡', '👑', '🔧', '⚙️', '🛠️', '🎯', '💎', '🚀', '🔥', '⭐'],
    'support': ['🆘', '💬', '📞', '🤝', '💫', '⚡', '🔔', '🎯', '🌟', '💎'],
    'user_info': ['👤', '📊', '📈', '💼', '🎯', '⚡', '🌟', '💎', '🚀', '⭐'],
    'promotion': ['📢', '🎉', '🔥', '⚡', '💫', '🌟', '🎯', '💎', '🚀', '⭐']
}

# Emoji tracking
last_emoji_change = datetime.now()
current_emoji_set = {}

def get_current_emoji(category):
    """Get current emoji for a category with 24-hour rotation"""
    global last_emoji_change, current_emoji_set
    
    # Check if 24 hours have passed
    if datetime.now() - last_emoji_change > timedelta(hours=24):
        current_emoji_set = {}
        last_emoji_change = datetime.now()
        logger.info("🎨 Emojis rotated! New 24-hour cycle started")
    
    # Get or set emoji for category
    if category not in current_emoji_set:
        if category in EMOJI_SETS:
            current_emoji_set[category] = random.choice(EMOJI_SETS[category])
        else:
            current_emoji_set[category] = '⭐'  # Default
    
    return current_emoji_set[category]

# ✅ UTILITY FUNCTIONS
def is_admin(user_id):
    """Check if user is admin"""
    return user_id == ADMIN_ID

def is_banned(user_id):
    """Check if user is banned"""
    return user_id in banned_users

def format_balance(amount):
    """Format balance with proper decimal places"""
    return f"{amount:.2f}"

def validate_amount(amount_str):
    """Validate and convert amount string to float"""
    try:
        amount = float(amount_str)
        if amount < 0:
            return None, "Amount cannot be negative"
        if amount > 999999:
            return None, "Amount too large"
        return amount, None
    except ValueError:
        return None, "Invalid amount format"

def get_user_balance(user_id):
    """Get user balance safely"""
    return user_balances.get(user_id, 0.0)

def add_user_balance(user_id, amount):
    """Add amount to user balance"""
    with data_lock:
        current_balance = user_balances.get(user_id, 0.0)
        user_balances[user_id] = current_balance + amount
        return user_balances[user_id]

def deduct_user_balance(user_id, amount):
    """Deduct amount from user balance"""
    with data_lock:
        current_balance = user_balances.get(user_id, 0.0)
        if current_balance >= amount:
            user_balances[user_id] = current_balance - amount
            return True, user_balances[user_id]
        return False, current_balance

# ✅ REFERRAL SYSTEM
def process_referral(referrer_id, referred_id):
    """Process referral bonus"""
    try:
        if referrer_id != referred_id and referred_id not in referral_data:
            referral_data[referred_id] = referrer_id
            bonus = 5.0  # Referral bonus
            add_user_balance(referrer_id, bonus)
            
            try:
                bot.send_message(
                    referrer_id,
                    f"🎉 Congratulations! You earned ₹{bonus} referral bonus!\n"
                    f"New user joined using your link."
                )
            except:
                pass
            return True
    except Exception as e:
        logger.error(f"Error processing referral: {e}")
    return False

# ✅ TASK MANAGEMENT
def generate_task_id():
    """Generate unique task ID"""
    return str(uuid.uuid4())[:8]

def add_task_to_section(section, task_data):
    """Add task to specific section"""
    if section in task_sections:
        task_data['id'] = generate_task_id()
        task_data['created_at'] = get_local_time()
        task_sections[section].append(task_data)
        save_data()
        return task_data['id']
    return None

def remove_task_from_section(section, task_id):
    """Remove task from section"""
    if section in task_sections:
        initial_count = len(task_sections[section])
        task_sections[section] = [t for t in task_sections[section] if t.get('id') != task_id]
        if len(task_sections[section]) < initial_count:
            save_data()
            return True
    return False

def get_available_tasks(user_id, section):
    """Get available tasks for user in section"""
    if section not in task_sections:
        return []
    
    user_completed = completed_tasks.get(user_id, set())
    available = []
    
    for task in task_sections[section]:
        task_id = task.get('id')
        if task_id and task_id not in user_completed:
            available.append(task)
    
    return available

def mark_task_completed(user_id, task_id):
    """Mark task as completed for user"""
    if user_id not in completed_tasks:
        completed_tasks[user_id] = set()
    completed_tasks[user_id].add(task_id)
    save_data()

# ✅ KEYBOARD GENERATORS
def create_main_keyboard():
    """Create main menu keyboard"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Get dynamic emojis
    task_emoji = get_current_emoji('task')
    balance_emoji = get_current_emoji('balance')
    submit_emoji = get_current_emoji('submit')
    withdraw_emoji = get_current_emoji('withdraw')
    referral_emoji = get_current_emoji('referral')
    support_emoji = get_current_emoji('support')
    user_info_emoji = get_current_emoji('user_info')
    promotion_emoji = get_current_emoji('promotion')
    
    markup.row(f"{task_emoji} Task", f"{balance_emoji} Balance", f"{submit_emoji} Submit Proof")
    markup.row(f"{withdraw_emoji} Withdraw", f"{referral_emoji} Referral", f"{support_emoji} Support")
    markup.row(f"{user_info_emoji} User Info", f"{promotion_emoji} Promotion")
    return markup

def create_admin_keyboard():
    """Create admin menu keyboard"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    admin_emoji = get_current_emoji('admin')
    
    markup.row(f"{admin_emoji} Add Task", f"{admin_emoji} Remove Task", f"{admin_emoji} Balance Mgmt")
    markup.row(f"{admin_emoji} User Stats", f"{admin_emoji} Withdrawals", f"{admin_emoji} Broadcast")
    markup.row(f"{admin_emoji} Ban User", f"{admin_emoji} Platform Stats", f"{admin_emoji} Bot Controls")
    markup.row("🔙 Back to Main")
    return markup

def create_task_sections_keyboard():
    """Create task sections keyboard"""
    markup = types.InlineKeyboardMarkup()
    
    task_emoji = get_current_emoji('task')
    
    markup.row(
        types.InlineKeyboardButton(f"{task_emoji} Watch Ads", callback_data="section_watch_ads"),
        types.InlineKeyboardButton(f"{task_emoji} App Downloads", callback_data="section_app_downloads")
    )
    markup.row(
        types.InlineKeyboardButton(f"{task_emoji} Promotional", callback_data="section_promotional")
    )
    
    return markup

# ✅ BOT COMMAND HANDLERS

@bot.message_handler(commands=['start'])
def start_command(message):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    first_name = message.from_user.first_name or "Friend"
    
    # Check if bot is frozen
    if bot_frozen and user_id != ADMIN_ID:
        bot.reply_to(message, "🚫 Bot is temporarily frozen for maintenance. Please try again later.")
        return
    
    # Check if user is banned
    if is_banned(user_id):
        bot.reply_to(message, "🚫 You have been banned from using this bot.")
        return
    
    # Process referral if present
    if message.text.startswith('/start ') and len(message.text.split()) > 1:
        referral_code = message.text.split()[1]
        try:
            referrer_id = int(referral_code)
            if referrer_id != user_id:  # Can't refer yourself
                process_referral(referrer_id, user_id)
        except ValueError:
            pass  # Invalid referral code
    
    # Initialize user balance if new user
    if user_id not in user_balances:
        user_balances[user_id] = 0.0
        save_data()
    
    # Get username for display
    bot_username = get_bot_username()
    
    # Welcome message with dynamic emojis
    task_emoji = get_current_emoji('task')
    balance_emoji = get_current_emoji('balance')
    
    welcome_text = f"""
👋 Welcome {first_name}!

{task_emoji} **Complete tasks and earn money!**
{balance_emoji} **Current Balance:** ₹{format_balance(get_user_balance(user_id))}

🎯 **Available Task Categories:**
• 📺 Watch Ads
• 📱 App Downloads  
• 📢 Promotional Tasks

💸 **Withdraw to UPI** when you have ₹10 or more
👥 **Refer friends** and earn ₹5 per referral

Use the menu below to get started!
"""
    
    bot.send_message(message.chat.id, welcome_text, 
                    reply_markup=create_main_keyboard(), 
                    parse_mode='Markdown')

@bot.message_handler(commands=['admin'])
def admin_command(message):
    """Handle /admin command"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, "🚫 Access denied. Admin only.")
        return
    
    admin_emoji = get_current_emoji('admin')
    admin_text = f"""
{admin_emoji} **ADMIN PANEL** {admin_emoji}

**User Management:**
• Add/Remove Tasks
• Manage User Balances
• View User Statistics
• Process Withdrawals

**Bot Controls:**
• Broadcast Messages
• Ban/Unban Users
• Platform Statistics
• Security Controls

Choose an option from the menu below:
"""
    
    bot.send_message(message.chat.id, admin_text, 
                    reply_markup=create_admin_keyboard(), 
                    parse_mode='Markdown')

@bot.message_handler(commands=[FREEZE_CODE.replace('/', '')])
def freeze_bot(message):
    """Freeze bot operations"""
    global bot_frozen, freeze_timestamp
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        return
    
    bot_frozen = True
    freeze_timestamp = get_local_time()
    
    admin_emoji = get_current_emoji('admin')
    bot.send_message(message.chat.id, 
                    f"{admin_emoji} **BOT FROZEN** {admin_emoji}\n\n"
                    f"🚫 All operations suspended\n"
                    f"⏰ Frozen at: {freeze_timestamp}\n\n"
                    f"Use `{UNFREEZE_CODE}` to unfreeze", 
                    parse_mode='Markdown')

@bot.message_handler(commands=[UNFREEZE_CODE.replace('/', '')])
def unfreeze_bot(message):
    """Unfreeze bot operations"""
    global bot_frozen, freeze_timestamp
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        return
    
    bot_frozen = False
    unfreeze_time = get_local_time()
    
    admin_emoji = get_current_emoji('admin')
    bot.send_message(message.chat.id, 
                    f"{admin_emoji} **BOT UNFROZEN** {admin_emoji}\n\n"
                    f"✅ All operations resumed\n"
                    f"⏰ Unfrozen at: {unfreeze_time}\n"
                    f"⏰ Was frozen at: {freeze_timestamp}", 
                    parse_mode='Markdown')

# ✅ MAIN MESSAGE HANDLERS

@bot.message_handler(func=lambda message: message.text and "Balance" in message.text)
def balance_command(message):
    """Handle balance request"""
    user_id = message.from_user.id
    
    if bot_frozen and not is_admin(user_id):
        bot.reply_to(message, "🚫 Bot is temporarily frozen for maintenance.")
        return
    
    if is_banned(user_id):
        bot.reply_to(message, "🚫 You have been banned from using this bot.")
        return
    
    balance = get_user_balance(user_id)
    balance_emoji = get_current_emoji('balance')
    
    balance_text = f"""
{balance_emoji} **Your Balance** {balance_emoji}

💰 **Current Balance:** ₹{format_balance(balance)}

{'✅ **You can withdraw!**' if balance >= 10 else '❌ **Minimum ₹10 needed to withdraw**'}

📊 **Statistics:**
• Total Tasks Completed: {len(completed_tasks.get(user_id, set()))}
• Referrals Made: {len([k for k, v in referral_data.items() if v == user_id])}

💡 **Tip:** Complete more tasks or refer friends to increase your balance!
"""
    
    bot.send_message(message.chat.id, balance_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text and "Task" in message.text)
def tasks_command(message):
    """Handle tasks request"""
    user_id = message.from_user.id
    
    if bot_frozen and not is_admin(user_id):
        bot.reply_to(message, "🚫 Bot is temporarily frozen for maintenance.")
        return
    
    if is_banned(user_id):
        bot.reply_to(message, "🚫 You have been banned from using this bot.")
        return
    
    task_emoji = get_current_emoji('task')
    
    task_text = f"""
{task_emoji} **Available Task Categories** {task_emoji}

Choose a category to see available tasks:

📺 **Watch Ads** - View advertisements and earn
📱 **App Downloads** - Download and try apps
📢 **Promotional** - Special promotional tasks

Select a category below:
"""
    
    bot.send_message(message.chat.id, task_text, 
                    reply_markup=create_task_sections_keyboard(), 
                    parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text and "Withdraw" in message.text)
def withdraw_command(message):
    """Handle withdraw request"""
    user_id = message.from_user.id
    
    if bot_frozen and not is_admin(user_id):
        bot.reply_to(message, "🚫 Bot is temporarily frozen for maintenance.")
        return
    
    if is_banned(user_id):
        bot.reply_to(message, "🚫 You have been banned from using this bot.")
        return
    
    balance = get_user_balance(user_id)
    withdraw_emoji = get_current_emoji('withdraw')
    
    if balance < 10:
        bot.send_message(message.chat.id, 
                        f"{withdraw_emoji} **Withdrawal Not Available**\n\n"
                        f"💰 Current Balance: ₹{format_balance(balance)}\n"
                        f"❌ Minimum ₹10.00 required\n"
                        f"💡 Complete more tasks to reach minimum!", 
                        parse_mode='Markdown')
        return
    
    awaiting_withdraw[user_id] = True
    
    withdraw_text = f"""
{withdraw_emoji} **Withdrawal Request** {withdraw_emoji}

💰 **Available Balance:** ₹{format_balance(balance)}
💳 **Minimum Amount:** ₹10.00
⚡ **Processing Time:** 24-48 hours

📝 **Instructions:**
Please send your withdrawal details in this format:

```
Amount: [amount]
UPI ID: [your_upi_id]
Name: [account_holder_name]
```

**Example:**
```
Amount: 50
UPI ID: example@paytm
Name: John Doe
```

Send your withdrawal request now:
"""
    
    bot.send_message(message.chat.id, withdraw_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.from_user.id in awaiting_withdraw and awaiting_withdraw[message.from_user.id])
def process_withdraw(message):
    """Process withdrawal request"""
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Parse withdrawal request
    try:
        lines = text.split('\n')
        withdrawal_data = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                withdrawal_data[key.strip().lower()] = value.strip()
        
        amount_str = withdrawal_data.get('amount', '')
        upi_id = withdrawal_data.get('upi id', '')
        name = withdrawal_data.get('name', '')
        
        if not amount_str or not upi_id or not name:
            bot.send_message(message.chat.id, 
                           "❌ Invalid format. Please use the exact format shown above.")
            return
        
        amount, error = validate_amount(amount_str)
        if error or amount is None:
            bot.send_message(message.chat.id, f"❌ {error or 'Invalid amount'}")
            return
        
        if amount < 10:
            bot.send_message(message.chat.id, "❌ Minimum withdrawal amount is ₹10.00")
            return
        
        current_balance = get_user_balance(user_id)
        if amount > current_balance:
            bot.send_message(message.chat.id, 
                           f"❌ Insufficient balance. Available: ₹{format_balance(current_balance)}")
            return
        
        # Create withdrawal request
        request_id = generate_task_id()
        withdrawal_requests[request_id] = {
            'user_id': user_id,
            'amount': amount,
            'upi_id': upi_id,
            'name': name,
            'status': 'pending',
            'created_at': get_local_time(),
            'username': message.from_user.username or 'Unknown'
        }
        
        # Deduct balance
        success, new_balance = deduct_user_balance(user_id, amount)
        if not success:
            bot.send_message(message.chat.id, "❌ Error processing withdrawal. Please try again.")
            del withdrawal_requests[request_id]
            return
        
        save_data()
        awaiting_withdraw[user_id] = False
        
        withdraw_emoji = get_current_emoji('withdraw')
        
        # Confirmation to user
        bot.send_message(message.chat.id, 
                        f"{withdraw_emoji} **Withdrawal Request Submitted** {withdraw_emoji}\n\n"
                        f"✅ Request ID: `{request_id}`\n"
                        f"💰 Amount: ₹{format_balance(amount)}\n"
                        f"💳 UPI ID: {upi_id}\n"
                        f"👤 Name: {name}\n"
                        f"💎 New Balance: ₹{format_balance(new_balance)}\n\n"
                        f"⏰ Processing time: 24-48 hours\n"
                        f"📞 Contact support if you have questions", 
                        parse_mode='Markdown')
        
        # Notify admin
        try:
            bot.send_message(ADMIN_ID, 
                           f"💸 **New Withdrawal Request**\n\n"
                           f"🆔 Request ID: `{request_id}`\n"
                           f"👤 User: {message.from_user.first_name} (@{message.from_user.username or 'No username'})\n"
                           f"💰 Amount: ₹{format_balance(amount)}\n"
                           f"💳 UPI ID: {upi_id}\n"
                           f"📝 Name: {name}\n"
                           f"⏰ Time: {get_local_time()}", 
                           parse_mode='Markdown')
        except:
            pass
    
    except Exception as e:
        logger.error(f"Error processing withdrawal: {e}")
        bot.send_message(message.chat.id, 
                        "❌ Error processing your request. Please try again.")
        awaiting_withdraw[user_id] = False

@bot.message_handler(func=lambda message: message.text and "Referral" in message.text)
def invite_command(message):
    """Handle invite friends request"""
    user_id = message.from_user.id
    
    if bot_frozen and not is_admin(user_id):
        bot.reply_to(message, "🚫 Bot is temporarily frozen for maintenance.")
        return
    
    if is_banned(user_id):
        bot.reply_to(message, "🚫 You have been banned from using this bot.")
        return
    
    bot_username = get_bot_username()
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    # Calculate referral stats
    referral_count = len([k for k, v in referral_data.items() if v == user_id])
    total_earned = referral_count * 5.0  # ₹5 per referral
    
    referral_emoji = get_current_emoji('referral')
    
    invite_text = f"""
{referral_emoji} **Invite Friends & Earn** {referral_emoji}

🎁 **Referral Bonus:** ₹5 per friend
👥 **Your Referrals:** {referral_count}
💰 **Total Earned:** ₹{format_balance(total_earned)}

🔗 **Your Referral Link:**
`{referral_link}`

📱 **Share this message:**
💰 Join this amazing money earning bot! Complete simple tasks and earn real money. Use my referral link to get started: {referral_link}

📋 **How it works:**
1. Share your referral link
2. When someone joins using your link
3. You earn ₹5 bonus instantly!
4. They can start earning too!

💡 **Tips:**
• Share in WhatsApp groups
• Post on social media
• Tell friends and family
"""
    
    bot.send_message(message.chat.id, invite_text, parse_mode='Markdown')

# ✅ FLASK API ENDPOINTS

@app.route(API_ENDPOINTS['add_balance'], methods=['POST'])
def api_add_balance():
    """API endpoint to add balance to user"""
    try:
        data = request.get_json()
        
        # Validate API key
        if data.get('api_key') != API_SECRET_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        
        user_id = data.get('user_id')
        amount = data.get('amount')
        
        if not user_id or not amount:
            return jsonify({'error': 'user_id and amount required'}), 400
        
        try:
            user_id = int(user_id)
            amount = float(amount)
        except ValueError:
            return jsonify({'error': 'Invalid user_id or amount format'}), 400
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        # Add balance
        new_balance = add_user_balance(user_id, amount)
        save_data()
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'amount_added': amount,
            'new_balance': new_balance,
            'timestamp': get_local_time()
        })
        
    except Exception as e:
        logger.error(f"API add_balance error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route(API_ENDPOINTS['check_balance'], methods=['POST'])
def api_check_balance():
    """API endpoint to check user balance"""
    try:
        data = request.get_json()
        
        # Validate API key
        if data.get('api_key') != API_SECRET_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({'error': 'Invalid user_id format'}), 400
        
        balance = get_user_balance(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'balance': balance,
            'timestamp': get_local_time()
        })
        
    except Exception as e:
        logger.error(f"API check_balance error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route(API_ENDPOINTS['user_info'], methods=['POST'])
def api_user_info():
    """API endpoint to get user information"""
    try:
        data = request.get_json()
        
        # Validate API key
        if data.get('api_key') != API_SECRET_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({'error': 'Invalid user_id format'}), 400
        
        balance = get_user_balance(user_id)
        completed_count = len(completed_tasks.get(user_id, set()))
        referral_count = len([k for k, v in referral_data.items() if v == user_id])
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'balance': balance,
            'completed_tasks': completed_count,
            'referrals': referral_count,
            'is_banned': user_id in banned_users,
            'timestamp': get_local_time()
        })
        
    except Exception as e:
        logger.error(f"API user_info error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ✅ RUN APPLICATION
if __name__ == "__main__":
    try:
        # Get bot username on startup
        get_bot_username()
        
        # Start Flask app in a separate thread
        flask_thread = threading.Thread(
            target=lambda: app.run(
                host='0.0.0.0', 
                port=int(os.environ.get('PORT', 5000)), 
                debug=False
            ), 
            daemon=True
        )
        flask_thread.start()
        logger.info("Flask API server started")
        
        # Start bot polling
        logger.info("Starting bot polling...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise
