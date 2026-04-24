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
VIDEO_URL = "https://raw.githubusercontent.com/kayusearn-cpu/bitassests/main/How%20BitAI%20works.mp4" 
CHANNEL_LINK = "https://t.me/affinity_bitai" 

# Links provided by user
BITAI_SIGNUP = "https://app.bitai.com.sg/h5/#/pages/sign/sign?invite=888"
BINANCE_SIGNUP = "https://accounts.binance.com/en/register?ref=1154159582"
MAS_EXCHANGE = "https://docs.google.com/forms/d/e/1FAIpQLSet5HhGpsXIcvTLMUFJpbhf7itvv1SZZ6czjtqFq6CP6NjQ3Q/viewform"
SEMINAR_LINK = "https://www.canva.com/design/DAG-1K3GDAE/n01T22Q9R7zW6l1kEVhaJA/edit"

# 2. Keyboard Builders
def channel_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📢 Join Our Community", url=CHANNEL_LINK)]])

def signup_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Create My BitAI Account", url=BITAI_SIGNUP)]])

def resource_list_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1️⃣ BitAI Account", url=BITAI_SIGNUP)],
        [InlineKeyboardButton("2️⃣ Binance Account", url=BINANCE_SIGNUP)],
        [InlineKeyboardButton("3️⃣ MAS Regulated Exchange", url=MAS_EXCHANGE)],
        [InlineKeyboardButton("4️⃣ Seminar Registration", url=SEMINAR_LINK)],
    ])

def social_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Telegram Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("📘 Setup Guide", url=CHANNEL_LINK)]
    ])

# 3. Automated Sequence Logic
async def user_automation_sequence(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    try:
        # Phase 1: Join Community Prompt (10 seconds)
        await asyncio.sleep(10)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hold on! 🛑 Before we dive in, make sure you don't miss any updates by joining our official community below:",
            reply_markup=channel_keyboard()
        )

        # Phase 2: Video Introduction (15 seconds - total elapsed 25s)
        await asyncio.sleep(15)
        await context.bot.send_message(chat_id=chat_id, text="🎥 <b>Introduction to our system by our Co-Founder:</b>", parse_mode="HTML")
        try:
            await context.bot.send_video(
                chat_id=chat_id, 
                video=VIDEO_URL, 
                caption="BitAI: Systematic Quantitative Trading",
                supports_streaming=True
            )
        except Exception as e:
            logging.error(f"Video delivery failed: {e}")

        # Phase 3: Sign Up Link (30 seconds - total elapsed 55s)
        await asyncio.sleep(30)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Ready to start your journey? Use the link below to create your account:",
            reply_markup=signup_keyboard()
        )

        # Phase 4: Useful Links (1 minute - total elapsed approx 2m)
        await asyncio.sleep(60)
        await context.bot.send_message(
            chat_id=chat_id,
            text="🛠 <b>Essential Resources:</b>\n\nHere are all the links you need to get fully set up and registered:",
            parse_mode="HTML",
            reply_markup=resource_list_keyboard()
        )

        # Phase 5: Reminder (2 hours)
        await asyncio.sleep(7200)
        await context.bot.send_message(
            chat_id=chat_id,
            text="🔔 <b>Just a quick reminder!</b>\n\nMake sure you've joined our channel and social platforms to stay updated with the latest market analysis.",
            parse_mode="HTML",
            reply_markup=social_keyboard()
        )

        # Phase 6: Eternal 5-hour Loop
        while True:
            await asyncio.sleep(18000) # 5 hours
            await context.bot.send_message(
                chat_id=chat_id,
                text="🔄 <b>Daily Process Recap:</b>\n\nEnsure your accounts are active and you've watched our strategy walkthrough.",
                parse_mode="HTML"
            )
            try:
                await context.bot.send_video(chat_id=chat_id, video=VIDEO_URL, caption="Recap: How BitAI Works")
            except: pass
            await context.bot.send_message(
                chat_id=chat_id,
                text="Quick Links:",
                reply_markup=resource_list_keyboard()
            )

    except Exception as e:
        logging.error(f"Automation sequence error: {e}")

# 4. Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    welcome_text = (
        "🤖 <b>BitAI Hub</b>\n\n"
        "BitAI is a quantitative trading software platform that applies mathematical modeling, "
        "statistical analysis, and algorithmic execution to help individual traders implement "
        "systematic approaches in fast-moving digital asset markets."
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")
    
    # Trigger the automated background tasks for this specific user
    asyncio.create_task(user_automation_sequence(context, chat_id))

# 5. Flask Health Check
flask_app = Flask(__name__)
@flask_app.route('/')
def health_check(): return "BitAI Automation Running"

# 6. Main Runner
async def run_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logging.error("TELEGRAM_BOT_TOKEN missing!")
        return

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

def main():
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))), daemon=True).start()
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
