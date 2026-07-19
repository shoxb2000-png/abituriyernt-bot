import asyncio
import os
import json
import logging
from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, Update, ReplyKeyboardMarkup, KeyboardButton

# Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

# =========================
# BOT TOKEN
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("\u274c TELEGRAM_TOKEN env o'zgaruvchisi topilmadi!")

# =========================
# FIREBASE
# =========================
firebase_ok = False
ref = None
try:
    creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    creds_path = os.getenv("FIREBASE_CREDENTIAL_PATH")

    if creds_json:
        creds_dict = json.loads(creds_json)
        # Fix escaped newlines in the private key (common Render env issue)
        if isinstance(creds_dict, dict) and "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(creds_dict)
    elif creds_path:
        cred = credentials.Certificate(creds_path)
    else:
        raise ValueError("\u274c Firebase credentials topilmadi!")

    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://abituriyent-16e96-default-rtdb.europe-west1.firebasedatabase.app"
    })
    ref = db.reference("phone_verifications")
    firebase_ok = True
    print("\u2705 Firebase muvaffaqiyatli ishga tushdi!")
except Exception as e:
    print(f"\u26a0\ufe0f Firebase xatosi (bot ishlashda davom etadi): {str(e)}")
    ref = None
    firebase_ok = False

# =========================
# BOT SETUP
# =========================
bot = Bot(token=TOKEN)
dp = Dispatcher()

# =========================
# HANDLERS
# =========================
@dp.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="\U0001f4f1 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer(
        "\U0001f44b Assalomu alaykum!\n\nRo'yxatdan o'tishni davom ettirish uchun telefon raqamingizni yuboring.",
        reply_markup=keyboard
    )

@dp.message(F.contact)
async def contact_handler(message: Message):
    if not firebase_ok or ref is None:
        await message.answer("\u26a0\ufe0f Baza vaqtincha ishlamayapti. Keyinroq urinib ko'ring.")
        return
    try:
        phone = message.contact.phone_number.replace("+", "")
        print(f"\U0001f4de Telefon olindi: {phone}")

        user = ref.child(phone).get()
        if user is None:
            print(f"\u274c Raqam bazada yo'q: {phone}")
            await message.answer(f"\u274c Ushbu telefon raqami topilmadi.\n\n\U0001f4de Izlangan raqam: {phone}")
            return

        user_data = user
        print(f"\U0001f4cb User data: {user_data}")

        if "code" not in user_data:
            print("\u274c 'code' field'i yo'q")
            await message.answer("\u274c Tasdiqlash kodi topilmadi.")
            return

        code = user_data.get("code")
        print(f"\u2705 Kod topildi: {code}")

        ref.child(phone).update({"verified": True})
        print(f"\u2705 Verified: {phone}")

        await message.answer(f"\u2705 Tasdiqlash kodi:\n\n\U0001f511 {code}")

    except Exception as e:
        print(f"\u26a0\ufe0f Xato: {str(e)}")
        await message.answer(f"\u26a0\ufe0f Xato yuz berdi:\n{str(e)}")

# =========================
# WEBHOOK ENDPOINT
# =========================
@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        update_data = request.get_json()
        update = Update(**update_data)
        await dp.feed_update(bot, update)
        return "ok", 200
    except Exception as e:
        print(f"\u274c Webhook xatosi: {e}")
        return "error", 500

# =========================
# HEALTH CHECK
# =========================
@app.route("/", methods=["GET"])
def health():
    return "\U0001f916 Bot ishlab turibdi!", 200

# =========================
# WEBHOOK REGISTRATION
# =========================
async def register_webhook():
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        print("\u26a0\ufe0f WEBHOOK_URL o'zgaruvchisi topilmadi")
        return
    try:
        await bot.set_webhook(webhook_url)
        print(f"\u2705 Webhook ro'yxatdan o'tkazildi: {webhook_url}")
    except Exception as e:
        print(f"\u26a0\ufe0f Webhook ro'yxatlash xatosi: {e}")

# =========================
# APP RUN
# =========================
if __name__ == "__main__":
    try:
        asyncio.run(register_webhook())
    except Exception as e:
        print(f"\u26a0\ufe0f Webhook init xatosi: {e}")

    port = int(os.getenv("PORT", 10000))
    print(f"\U0001f680 Web server {port}-portda ishga tushmoqda...")
    app.run(host="0.0.0.0", port=port, debug=False)
