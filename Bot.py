import os
import logging
import asyncio
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from flask import Flask

# 1. Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- CONFIGURATION ---
# Replace this with your actual video file_id (Get it by sending the video to the bot and checking logs)
VIDEO_FILE_ID = "YOUR_VIDEO_FILE_ID_HERE" 
CHANNEL_LINK = "https://t.me/YourChannelUsername" # Replace with your actual channel link

# Links provided by user
BITAI_SIGNUP = "https://app.bitai.com.sg/h5/#/pages/sign/sign?invite=888"
BINANCE_SIGNUP = "https://accounts.binance.com/en/register?ref=1154159582"
MAS_EXCHANGE = "https://docs.google.com/forms/d/e/1FAIpQLSet5HhGpsXIcvTLMUFJpbhf7itvv1SZZ6czjtqFq6CP6NjQ3Q/viewform"
SEMINAR_LINK = "https://www.canva.com/design/DAG-1K3GDAE/n01T22Q9R7zW6l1kEVhaJA/edit"

# 2. Content Library
CONTENT = {
    "basics": {
        "text": (
            "📚 <b>AI Trading Basics</b>\n\n"
            "<b>Lesson 1: What is Algorithmic Trading?</b>\n"
            "Algorithmic trading uses computer programs to execute trades based on predefined rules.\n\n"
            "📌 <b>Key Takeaway:</b> AI removes emotion from trading and replaces it with data-driven rules."
        )
    }
    # ... (Other content categories remain the same as your original code)
}

# 3. Keyboard Builders
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Official Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("📚 AI Trading Basics", callback_data="basics"),
         InlineKeyboardButton("🤖 How AI Reads Markets", callback_data="reads_markets")],
        [InlineKeyboardButton("📊 AI Decision Tools", callback_data="decision_tools"),
         InlineKeyboardButton("🧠 AI Strategy Fundamentals", callback_data="strategy")],
        [InlineKeyboardButton("📈 Case Studies", callback_data="case_studies"),
         InlineKeyboardButton("❓ Quiz", callback_data="quiz_start")],
    ])

def resource_list_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1️⃣ Create my FREE BitAI Account!", url=BITAI_SIGNUP)],
        [InlineKeyboardButton("2️⃣ Create a Free Binance Account", url=BINANCE_SIGNUP)],
        [InlineKeyboardButton("3️⃣ Register with MAS Regulated Exchange", url=MAS_EXCHANGE)],
        [InlineKeyboardButton("4️⃣ Sign up for BitAI seminar (FREE)", url=SEMINAR_LINK)],
        [InlineKeyboardButton("📘 BitAI Setup Guide", url=CHANNEL_LINK)]
    ])

# 4. Automated Delivery Tasks
async def scheduled_delivery(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Handles the 3-minute and 5-minute automated messages."""
    try:
        # Wait 3 minutes (180 seconds)
        await asyncio.sleep(180)
        await context.bot.send_message(
            chat_id=chat_id,
            text="🎥 <b>Check out these exclusive videos!</b>\n\nWhile you wait, watch how we set up our AI systems for success.",
            parse_mode="HTML"
        )
        # Attempt to send the video file
        try:
            await context.bot.send_video(chat_id=chat_id, video=VIDEO_FILE_ID, caption="BitAI Strategy Walkthrough")
        except Exception as e:
            logging.error(f"Failed to send video: {e}. Ensure VIDEO_FILE_ID is correct.")
            await context.bot.send_message(chat_id=chat_id, text="[Video content is being processed, please check our channel in the meantime!]")

        # Wait another 2 minutes (Total 5 minutes from start)
        await asyncio.sleep(120)
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "🚀 <b>Ready to take the next step?</b>\n\n"
                "Here is your essential resource list to get started with BitAI today:"
            ),
            parse_mode="HTML",
            reply_markup=resource_list_keyboard()
        )
    except Exception as e:
        logging.error(f"Error in scheduled delivery: {e}")

# 5. Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Welcome Message
    text = (
        f"🤖 <b>Welcome to BitAI Learning Hub</b>\n\n"
        f"I've sent you a special invitation to our <b>Official Channel</b> below. "
        f"Please join to stay updated with live signals!\n\n"
        f"🎯 <b>Your learning journey starts now.</b>"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu_keyboard())
    
    # Trigger the background timer for this user
    asyncio.create_task(scheduled_delivery(context, chat_id))

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 Choose a topic below to begin learning:",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )

# (Additional handlers like help_command, about_command, button_handler remain consistent with your logic)

# 6. Callback Query Handler (Simplified)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu":
        await query.edit_message_text("🎯 Choose a topic:", reply_markup=main_menu_keyboard())
    elif data in CONTENT:
        await query.edit_message_text(CONTENT[data]["text"], parse_mode="HTML", 
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="menu")]]))
    elif data == "quiz_start":
        await query.edit_message_text("🧠 Starting Quiz...")
        # (Add your quiz logic here as per original code)

# 7. Flask Health Check
flask_app = Flask(__name__)
@flask_app.route('/')
def health_check():
    return "BitAI Learning Hub is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

# 8. Main Runner
async def run_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logging.error("TELEGRAM_BOT_TOKEN is missing!")
        return

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logging.info("BitAI Bot started...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == '__main__':
    main()
