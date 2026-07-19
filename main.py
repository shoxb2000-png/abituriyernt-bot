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
from threading import Thread

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
    raise ValueError("❌ TELEGRAM_TOKEN env o'zgaruvchisi topilmadi!")

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
        # Fix escaped newlines in the private key
        if isinstance(creds_dict, dict) and "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(creds_dict)
    elif creds_path:
        cred = credentials.Certificate(creds_path)
    else:
        raise ValueError("❌ Firebase credentials topilmadi!")
    
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://abituriyent-16e96-default-rtdb.europe-west1.firebasedatabase.app"
    })
    ref = db.reference("phone_verifications")
    firebase_ok = True
    print("✅ Firebase muvaffaqiyatli ishga tushdi!")
except Exception as e:
    print(f"⚠️ Firebase xatosi: {str(e)}")
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
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer(
        "👋 Assalomu alaykum!\n\nRo'yxatdan o'tishni davom ettirish uchun telefon raqamingizni yuboring.",
        reply_markup=keyboard
    )

@dp.message(F.contact)
async def contact_handler(message: Message):
    if not firebase_ok or ref is None:
        await message.answer("⚠️ Baza vaqtincha ishlamayapti. Keyinroq urinib ko'ring.")
        return
    
    try:
        phone = message.contact.phone_number.replace("+", "")
        print(f"📞 Telefon olindi: {phone}")

        # Firebase-dan qidirish
        user = ref.child(phone).get()
        
        if user.val() is None:
            print(f"❌ Raqam bazada yo'q: {phone}")
            await message.answer(f"❌ Ushbu telefon raqami topilmadi.\n\n📞 Izlangan raqam: {phone}")
            return

        user_data = user.val()
        print(f"📋 User data: {user_data}")
        
        if "code" not in user_data:
            print("❌ 'code' field'i yo'q")
            await message.answer("❌ Tasdiqlash kodi topilmadi.")
            return

        code = user_data.get("code")
        print(f"✅ Kod topildi: {code}")
        
        # Verified qilib markerlash
        ref.child(phone).update({"verified": True})
        print(f"✅ Verified: {phone}")

        await message.answer(f"✅ Tasdiqlash kodi:\n\n🔑 {code}")
        
    except Exception as e:
        print(f"⚠️ Xato: {str(e)}")
        await message.answer(f"⚠️ Xato yuz berdi:\n{str(e)}")

# =========================
# HEALTH CHECK
# =========================
@app.route("/", methods=["GET"])
def health():
    return "🤖 Bot ishlab turibdi!", 200

# =========================
# POLLING LOOP (separate thread)
# =========================
async def start_polling():
    """Bot polling rejimida ishga tushirish"""
    print("✅ Bot polling rejimida ishga tushdi...")
    await dp.start_polling(bot, polling_timeout=10)

def run_polling():
    """Separate thread-da polling ishga tushirish"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_polling())

# =========================
# APP RUN
# =========================
if __name__ == "__main__":
    # Polling-ni separate thread-da ishga tushirish
    polling_thread = Thread(target=run_polling, daemon=True)
    polling_thread.start()
    
    port = int(os.getenv("PORT", 5000))
    print(f"✅ Bot ishga tushdi")
    print(f"🚀 Flask server {port}-portda ishga tushmoqda...")
    
    # Flask server
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
