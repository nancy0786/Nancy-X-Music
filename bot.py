from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot token
TOKEN = "8193433946:AAE3XMndNhtEc_FVPc3SNQtsIEanW1rpMr4"
bot = Bot(token=TOKEN)

# Store active group chat IDs
active_groups = set()

def get_group_name(chat):
    """Fetch the group name dynamically."""
    return chat.title if chat.title else "this group"

def get_admins(chat_id):
    """Fetch a list of group admins."""
    try:
        admins = bot.get_chat_administrators(chat_id)
        return [admin.user.id for admin in admins]
    except:
        return []

def send_good_morning():
    """Send a Good Morning message to all active groups."""
    for chat_id in active_groups:
        group_name = get_group_name(bot.get_chat(chat_id))
        bot.send_message(chat_id=chat_id, text=f"""
🌞 **Good Morning, {group_name}!** ☕✨  

May your day be filled with **happiness, success, and endless positivity**! 💖🌿  
🌅 **Rise and shine!** A new day brings **new opportunities**—embrace them with a **smile!** 😊  

🚀 Have a **productive, joyful, and amazing** day ahead! 🌸💫  
""", parse_mode=ParseMode.MARKDOWN)

def send_good_night():
    """Send a Good Night message to all active groups."""
    for chat_id in active_groups:
        group_name = get_group_name(bot.get_chat(chat_id))
        bot.send_message(chat_id=chat_id, text=f"""
🌙 **Good Night, {group_name}!** ✨💤  

As the stars twinkle above, may **peace and happiness** fill your heart. 💖🌌  
😴 **Close your eyes,** forget today’s worries, and drift into a night of sweet dreams! 🌠  

🌿 **Rest well,** recharge, and wake up stronger tomorrow!  
🚀 **Sleep tight and wake up refreshed!** 🌙💖  
""", parse_mode=ParseMode.MARKDOWN)

def track_groups(update: Update, context: CallbackContext):
    """Track groups where the bot is added."""
    chat = update.message.chat
    if chat.type in ["group", "supergroup"]:
        active_groups.add(chat.id)
        logger.info(f"Bot added to group: {chat.title} (ID: {chat.id})")

def admin_triggered_messages(update: Update, context: CallbackContext):
    """Respond when an admin sends 'Good Morning', 'Good Night', 'Good Evening', or 'Good Afternoon'."""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text.lower()

    if user_id in get_admins(chat_id):
        if "good morning" in text:
            send_good_morning()
        elif "good night" in text:
            send_good_night()
        elif "good evening" in text:
            group_name = get_group_name(bot.get_chat(chat_id))
            bot.send_message(chat_id=chat_id, text=f"🌆 **Good Evening, {group_name}!** 🌇✨\nHope you're having a relaxing evening! 💫", parse_mode=ParseMode.MARKDOWN)
        elif "good afternoon" in text:
            group_name = get_group_name(bot.get_chat(chat_id))
            bot.send_message(chat_id=chat_id, text=f"🌞 **Good Afternoon, {group_name}!** 🌿✨\nWishing you a bright and joyful afternoon! 🌻", parse_mode=ParseMode.MARKDOWN)

def main():
    """Start the bot and schedule daily messages."""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Track groups automatically when bot is added
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, track_groups))

    # Admin-triggered messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, admin_triggered_messages))

    # Scheduler for automatic messages
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_good_morning, "cron", hour=7, minute=0)
    scheduler.add_job(send_good_night, "cron", hour=22, minute=0)
    scheduler.start()

    # Keep bot running
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
