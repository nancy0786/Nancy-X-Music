import os
import logging
from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import yt_dlp

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot token
TOKEN = "YOUR_BOT_TOKEN"
bot = Bot(token=TOKEN)

# Store active group chat IDs
active_groups = set()
music_queue = {}

def get_group_name(chat):
    """Fetch the group name dynamically."""
    return chat.title if chat.title else "this group"

def send_good_morning():
    """Send a Good Morning message to all active groups."""
    for chat_id in active_groups:
        group_name = get_group_name(bot.get_chat(chat_id))
        bot.send_message(chat_id=chat_id, text=f"""
🌞 **Good Morning, {group_name}!** ☕✨  
May your day be filled with happiness, success, and positivity! 🚀
""", parse_mode=ParseMode.MARKDOWN)

def send_good_night():
    """Send a Good Night message to all active groups."""
    for chat_id in active_groups:
        group_name = get_group_name(bot.get_chat(chat_id))
        bot.send_message(chat_id=chat_id, text=f"""
🌙 **Good Night, {group_name}!** ✨💤  
Rest well, recharge, and wake up stronger tomorrow! 🌟
""", parse_mode=ParseMode.MARKDOWN)

def track_groups(update: Update, context: CallbackContext):
    """Track groups where the bot is added."""
    chat = update.message.chat
    if chat.type in ["group", "supergroup"]:
        active_groups.add(chat.id)
        logger.info(f"Bot added to group: {chat.title} (ID: {chat.id})")

def admin_triggered_greetings(update: Update, context: CallbackContext):
    """If an admin sends a greeting message, the bot replies automatically."""
    user = update.message.from_user
    chat_id = update.message.chat_id
    admins = [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
    
    if user.id in admins:
        text = update.message.text.lower()
        if any(word in text for word in ["good morning", "gm"]):
            send_good_morning()
        elif any(word in text for word in ["good night", "gn"]):
            send_good_night()

def help_command(update: Update, context: CallbackContext):
    """Send a list of available commands."""
    help_text = """📜 **Available Commands:**  
🎵 **Music Controls:**  
- `/play <song_url>` → Play a song from YouTube  
- `/queue <song_url>` → Add a song to the queue  
- `/showqueue` → Show current queue  
- `/control pause` → Pause the music  
- `/control resume` → Resume music  
- `/control skip` → Skip to the next song  
- `/stop` → Stop music playback  

📥 **Download Music:**  
- `/download <YouTube URL>` → Convert video to MP3  

🕒 **Scheduled Messages:**  
- (Auto) Good Morning at **7 AM**  
- (Auto) Good Night at **10 PM**  

👑 **Admin Triggers:**  
- If an admin sends "Good Morning" or "Good Night," the bot replies  

ℹ️ **General:**  
- `/help` → Show this command list  
"""
    update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

def download_audio(update: Update, context: CallbackContext):
    """Download YouTube video as MP3."""
    if not context.args:
        update.message.reply_text("Usage: `/download <YouTube_URL>`", parse_mode=ParseMode.MARKDOWN)
        return

    url = context.args[0]
    save_path = "Nancys Audio"
    os.makedirs(save_path, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{save_path}/%(title)s.%(ext)s",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    update.message.reply_text(f"✅ Download completed! Check `{save_path}` folder.", parse_mode=ParseMode.MARKDOWN)

def main():
    """Start the bot and schedule daily messages."""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command Handlers
    dp.add_handler(CommandHandler("start", track_groups))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("download", download_audio))

    # Auto-Response for Admin Greetings
    dp.add_handler(MessageHandler(Filters.text & Filters.chat_type.groups, admin_triggered_greetings))

    # Scheduler for Good Morning/Night Messages
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_good_morning, "cron", hour=7, minute=0)
    scheduler.add_job(send_good_night, "cron", hour=22, minute=0)
    scheduler.start()

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()