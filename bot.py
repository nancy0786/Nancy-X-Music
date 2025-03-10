import logging
import time
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from yt_dlp import YoutubeDL

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot token
TOKEN = "8193433946:AAE3XMndNhtEc_FVPc3SNQtsIEanW1rpMr4"
GROUP_ID = -1002335769239  # Replace with your group/channel ID

bot = Bot(token=TOKEN)
scheduler = BackgroundScheduler()

# Playlist storage
playlists = {}

# Fetch group admins
def get_admins(chat_id):
    """Fetch the list of admins (including owner) from the group."""
    admins = bot.get_chat_administrators(chat_id)
    return [admin.user.id for admin in admins]

# Good Morning & Good Night Messages
def send_good_morning():
    """Send a good morning message to all admins and group."""
    message = "🌞 **Good Morning, Everyone!** ☕✨\nMay your day be filled with happiness and success! 😊🚀"
    bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")

def send_good_night():
    """Send a good night message to all admins and group."""
    message = "🌙 **Good Night, Everyone!** ✨💤\nRest well and wake up refreshed! 🌟💖"
    bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")

# Re-send morning/night messages if an admin sends it manually
def check_greetings(update: Update, context: CallbackContext):
    """Check if an admin sends a morning/night greeting and resend the formatted message."""
    user_id = update.message.from_user.id
    admins = get_admins(GROUP_ID)
    text = update.message.text.lower()

    if user_id in admins:
        if "good morning" in text:
            send_good_morning()
        elif "good night" in text:
            send_good_night()
        elif "good afternoon" in text:
            bot.send_message(chat_id=GROUP_ID, text="🌅 **Good Afternoon, Everyone!** ☕💖", parse_mode="Markdown")
        elif "good evening" in text:
            bot.send_message(chat_id=GROUP_ID, text="🌆 **Good Evening, Everyone!** 🌟🎶", parse_mode="Markdown")

# Welcome & Farewell Messages
def welcome_message(update: Update, context: CallbackContext):
    """Send a welcome message when a user joins."""
    user = update.message.new_chat_members[0]
    message = f"🌟 Welcome to the group, {user.first_name}! 🎉 Enjoy your stay! 🚀"
    bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")

def farewell_message(update: Update, context: CallbackContext):
    """Send a farewell message when a user leaves."""
    user = update.message.left_chat_member
    message = f"💔 Goodbye, {user.first_name}! We will miss you! 😢💖"
    bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")

# Playlist Management
def create_playlist(update: Update, context: CallbackContext):
    """Allows admins to create playlists."""
    user_id = update.message.from_user.id
    if user_id not in get_admins(GROUP_ID):
        return update.message.reply_text("❌ Only admins can create playlists.")

    playlist_name = " ".join(context.args)
    if not playlist_name:
        return update.message.reply_text("📌 Please specify a playlist name.")

    playlists[playlist_name] = []
    update.message.reply_text(f"✅ Playlist '{playlist_name}' created!")

def add_song(update: Update, context: CallbackContext):
    """Allows admins to add songs to a playlist."""
    user_id = update.message.from_user.id
    if user_id not in get_admins(GROUP_ID):
        return update.message.reply_text("❌ Only admins can add songs.")

    if len(context.args) < 2:
        return update.message.reply_text("📌 Usage: /addsong <playlist_name> <song_url>")

    playlist_name, song_url = context.args[0], context.args[1]
    if playlist_name not in playlists:
        return update.message.reply_text("❌ Playlist does not exist.")

    playlists[playlist_name].append(song_url)
    update.message.reply_text(f"🎵 Song added to '{playlist_name}'!")

def delete_playlist(update: Update, context: CallbackContext):
    """Allows admins to delete playlists."""
    user_id = update.message.from_user.id
    if user_id not in get_admins(GROUP_ID):
        return update.message.reply_text("❌ Only admins can delete playlists.")

    playlist_name = " ".join(context.args)
    if playlist_name in playlists:
        del playlists[playlist_name]
        update.message.reply_text(f"🗑 Playlist '{playlist_name}' deleted!")
    else:
        update.message.reply_text("❌ Playlist not found.")

def view_playlist(update: Update, context: CallbackContext):
    """Allows users to view and play songs from a playlist."""
    if not context.args:
        return update.message.reply_text("📌 Usage: /viewplaylist <playlist_name>")

    playlist_name = " ".join(context.args)
    if playlist_name not in playlists:
        return update.message.reply_text("❌ Playlist not found.")

    song_list = playlists[playlist_name]
    if not song_list:
        return update.message.reply_text(f"📂 Playlist '{playlist_name}' is empty.")

    page = 0
    songs_per_page = 10
    total_pages = (len(song_list) // songs_per_page) + 1

    def get_page(page):
        start = page * songs_per_page
        end = start + songs_per_page
        return song_list[start:end]

    message = f"📂 **Playlist: {playlist_name}** (Page {page+1}/{total_pages})\n\n"
    message += "\n".join([f"{i+1}. {song}" for i, song in enumerate(get_page(page))])
    bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")

# Start Bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Scheduled tasks
    scheduler.add_job(send_good_morning, "cron", hour=7, minute=0)
    scheduler.add_job(send_good_night, "cron", hour=22, minute=0)
    scheduler.start()

    # Handlers
    dp.add_handler(CommandHandler("createplaylist", create_playlist))
    dp.add_handler(CommandHandler("addsong", add_song))
    dp.add_handler(CommandHandler("deleteplaylist", delete_playlist))
    dp.add_handler(CommandHandler("viewplaylist", view_playlist))
    dp.add_handler(MessageHandler(Filters.text & Filters.chat(GROUP_ID), check_greetings))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome_message))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, farewell_message))

    # Start bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
