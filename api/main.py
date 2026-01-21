import os
import json
import logging
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# =====================
# ENV VARIABLES
# =====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DISCUSSION_GROUP_ID = int(os.environ.get("DISCUSSION_GROUP_ID"))
REPORT_GROUP_ID = os.environ.get("REPORT_GROUP_ID")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# =====================
# CONFIG
# =====================
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

MESSAGE_TEXT = CONFIG["message_text"]
BUTTONS = CONFIG["buttons"]

# =====================
# LOGGING
# =====================
logging.basicConfig(level=logging.INFO)

# =====================
# FLASK APP
# =====================
app = Flask(__name__)

# =====================
# HELPERS
# =====================
def build_keyboard(bot_username):
    keyboard = InlineKeyboardMarkup()
    for btn in BUTTONS:
        if btn["text"] == "Trade Guard":
            url = f"https://t.me/{bot_username}?start=trade_guard"
        elif btn["text"] == "Report Scammer":
            url = f"https://t.me/{bot_username}?start=report_scammer"
        else:
            url = btn["url"]
        keyboard.add(InlineKeyboardButton(btn["text"], url=url))
    return keyboard

# =====================
# HANDLER FUNCTIONS
# =====================
def handle_start(message, param=None):
    user_name = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    bot_username = bot.get_me().username

    if param == "trade_guard":
        text = (
            f"Hi! 👋 {user_name} untuk menggunakan Trade Guard silahkan hubungi admin:\n\n"
            "@spcydick\n"
            "@fallinlauvy\n\n"
            "🛡️ | Safety Steps ✔\nPastikan sebelum transaksi menggunakan rekber untuk cek username admin di atas!"
        )
        bot.send_message(message.chat.id, text)
        return
    elif param == "report_scammer":
        bot.send_message(message.chat.id, f"Hi! 👋 {user_name} silakan kirimkan username pelaku beserta bukti.")
        bot.register_next_step_handler(message, handle_report)
        return

    # normal start
    keyboard = build_keyboard(bot_username)
    bot.send_photo(
        message.chat.id,
        photo="https://i.postimg.cc/3wdBs6LJ/Asset-2xxxhdpi.png",
        caption="<b>Pusat Pengaduan & Layanan Transaksi Resmi</b>\n\nKami berkomitmen menciptakan lingkungan transaksi yang aman.",
        reply_markup=keyboard
    )

def handle_report(message):
    user_name = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    report_content = f"Report dari {user_name}:\n"

    if message.text:
        report_content += f"• {message.text}"
    elif message.photo:
        report_content += "• [Foto dikirim]"
    elif message.document:
        report_content += f"• [Dokumen dikirim: {message.document.file_name}]"
    else:
        report_content += "• [Media tanpa caption]"

    # kirim ke report group
    if REPORT_GROUP_ID:
        bot.send_message(REPORT_GROUP_ID, report_content)

    bot.send_message(message.chat.id, "Terima kasih, laporan telah diterima!")

# =====================
# WEBHOOK ROUTE
# =====================
@app.route("/api/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running!"

# =====================
# HANDLER REGISTRATION
# =====================
@bot.message_handler(commands=["start"])
def on_start(message):
    param = message.text.split()[1] if len(message.text.split()) > 1 else None
    handle_start(message, param)

# =====================
# GROUP FORWARD HANDLER
# =====================
@bot.message_handler(func=lambda m: m.chat.id == DISCUSSION_GROUP_ID)
def on_group_forward(message):
    bot_username = bot.get_me().username
    keyboard = build_keyboard(bot_username)
    bot.send_message(message.chat.id, MESSAGE_TEXT, reply_markup=keyboard)

