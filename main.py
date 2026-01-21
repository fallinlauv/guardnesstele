import os
import json
import logging
from flask import Flask, request
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# =====================
# LOAD ENV
# =====================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DISCUSSION_GROUP_ID = os.getenv("DISCUSSION_GROUP_ID")
REPORT_GROUP_ID = os.getenv("REPORT_GROUP_ID")

# =====================
# LOAD CONFIG
# =====================
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

MESSAGE_TEXT = CONFIG["message_text"]
BUTTONS = CONFIG["buttons"]

# =====================
# LOGGING
# =====================
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

app = Flask(__name__)
# Initialize Bot and Application without starting polling
application = Application.builder().token(BOT_TOKEN).build()

# =====================
# HANDLERS
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    if context.args:
        param = context.args[0]
        user_name = update.effective_user.mention_html()
        
        if param == "trade_guard":
            trade_guard_text = (
                f"<i>Hi!</i> ðŸ‘‹ {user_name} untuk menggunakan Trade Guard silahkan hubungi admin di bawah ini\n\n"
                "@spcydick\n"
                "@fallinlauvy\n\n"
                "<blockquote>"
                "ðŸ§¢ | <b>Safety Steps</b> âœ¨\n"
                "Pastikan sebelum transaksi menggunakan rekber untuk cek username admin di atas, dan berhati-hati lah terhadap akun palsu!"
                "</blockquote>"
            )
            await update.message.reply_text(trade_guard_text, parse_mode="HTML")
            return
            
        elif param == "report_scammer":
            context.user_data["awaiting_report"] = True
            report_scammer_text = (
                f"<i>Hi!</i> ðŸ‘‹ {user_name} silakan kirimkan username pelaku beserta bukti foto/screenshot di bawah ini untuk kami tindak lanjuti segera."
            )
            await update.message.reply_text(report_scammer_text, parse_mode="HTML")
            return

    # Create keyboard from config
    keyboard = []
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
    except Exception:
        bot_username = "bot_username"  # Fallback
        
    for btn in BUTTONS:
        if btn["text"] == "Trade Guard":
            url = f"https://t.me/{bot_username}?start=trade_guard"
            keyboard.append([InlineKeyboardButton(btn["text"], url=url)])
        elif btn["text"] == "Report Scammer":
            url = f"https://t.me/{bot_username}?start=report_scammer"
            keyboard.append([InlineKeyboardButton(btn["text"], url=url)])
        else:
            keyboard.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
        
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo="https://i.postimg.cc/3wdBs6LJ/Asset-2xxxhdpi.png",
        caption=(
            "<blockquote>"
            "<b>Pusat Pengaduan &amp; Layanan Transaksi Resmi</b>\n\n"
            "Kami berkomitmen menciptakan lingkungan transaksi yang "
            "transparan dan bebas dari penipuan."
            "</blockquote>"
        ),
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private" and context.user_data.get("awaiting_report"):
        if "report_messages" not in context.user_data:
            context.user_data["report_messages"] = []
        
        if update.message.text:
            context.user_data["report_messages"].append(f"â€¢ {update.message.text}")
        elif update.message.caption:
            context.user_data["report_messages"].append(f"â€¢ [Media] {update.message.caption}")
        else:
            context.user_data["report_messages"].append("â€¢ [Media tanpa caption]")

        old_msg_id = context.user_data.get("last_report_msg_id")
        if old_msg_id:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=old_msg_id)
            except Exception:
                pass
        
        keyboard = [[InlineKeyboardButton("Submit", callback_data="submit_report")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        sent_msg = await update.message.reply_text("ðŸ“¥ Laporan di terima", reply_markup=reply_markup)
        context.user_data["last_report_msg_id"] = sent_msg.message_id
        return

    if str(update.effective_chat.id) != DISCUSSION_GROUP_ID:
        return

    if not update.message.is_automatic_forward and not update.message.forward_from_chat:
        return

    # Create keyboard from config
    keyboard = []
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
    except Exception:
        bot_username = "bot_username"  # Fallback
        
    for btn in BUTTONS:
        if btn["text"] == "Trade Guard":
            url = f"https://t.me/{bot_username}?start=trade_guard"
            keyboard.append([InlineKeyboardButton(btn["text"], url=url)])
        elif btn["text"] == "Report Scammer":
            url = f"https://t.me/{bot_username}?start=report_scammer"
            keyboard.append([InlineKeyboardButton(btn["text"], url=url)])
        else:
            keyboard.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
        
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=MESSAGE_TEXT,
            reply_to_message_id=update.message.message_id,
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Gagal mengirim komentar: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_name = update.effective_user.mention_html()
    
    if query.data == "trade_guard":
        trade_guard_text = (
            f"<i>Hi!</i> ðŸ‘‹ {user_name} untuk menggunakan Trade Guard silahkan hubungi admin di bawah ini\n\n"
            "@spcydick\n"
            "@fallinlauvy\n\n"
            "<blockquote>"
            "ðŸ§¢ | <b>Safety Steps</b> âœ¨\n"
            "Pastikan sebelum transaksi menggunakan rekber untuk cek username admin di atas, dan berhati-hati lah terhadap akun palsu!"
            "</blockquote>"
        )
        await query.message.reply_text(trade_guard_text, parse_mode="HTML")
        
    elif query.data == "report_scammer":
        context.user_data["awaiting_report"] = True
        report_scammer_text = (
            f"<i>Hi!</i> ðŸ‘‹ {user_name} silakan kirimkan username pelaku beserta bukti foto/screenshot di bawah ini untuk kami tindak lanjuti segera."
        )
        await query.message.reply_text(report_scammer_text, parse_mode="HTML")

    elif query.data == "submit_report":
        context.user_data["awaiting_report"] = False
        context.user_data.pop("last_report_msg_id", None)
        
        report_content = context.user_data.pop("report_messages", [])
        if report_content and REPORT_GROUP_ID:
            user = update.effective_user
            header = f"ðŸš¨ <b>LAPORAN SCAM BARU</b>\n\n"
            header += f"<b>Dari:</b> {user.mention_html()} (<code>{user.id}</code>)\n"
            header += f"<b>Isi Laporan:</b>\n\n"
            full_report = header + "\n".join(report_content)
            
            try:
                await context.bot.send_message(
                    chat_id=REPORT_GROUP_ID,
                    text=full_report,
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"Gagal mengirim laporan ke grup: {e}")

        await query.message.edit_text(
            "Terima kasih atas informasinya, kami akan segera memproses dan menangani masalah ini untuk menjaga keamanan bersama."
        )

# =====================
# VERCEL ENTRY POINT
# =====================

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ATTACHMENT, handle_message))

@app.route('/api/webhook', methods=['POST'])
async def webhook():
    if request.method == "POST":
        try:
            update_data = request.get_json(force=True)
            logging.info(f"Webhook received update: {update_data}")
            update = Update.de_json(update_data, application.bot)
            
            # Use background task to handle update
            asyncio.create_task(application.process_update(update))
            
            return "OK", 200
        except Exception as e:
            logging.error(f"Error processing webhook: {e}")
            return "Error", 500
    return "Method not allowed", 405

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == "__main__":
    # For local testing, use polling or run the flask app
    # In Vercel, only the 'app' instance is used
    import asyncio
    async def run_local():
        async with application:
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            app.run(host="0.0.0.0", port=5000)
    
    asyncio.run(run_local())
