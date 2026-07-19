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
    raise ValueError("❌ TELEGRAM_TOKEN env o'zgaruvchisi topilmadi!")

# =========================
# FIREBASE
# =========================
try:
    creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    creds_path = os.getenv("FIREBASE_CREDENTIAL_PATH")
    
    if creds_json:
        cred = credentials.Certificate(json.loads(creds_json))
    elif creds_path:
        cred = credentials.Certificate(creds_path)
    else:
        raise ValueError("❌ Firebase credentials topilmadi!")
    
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://abituriyent-16e96-default-rtdb.europe-west1.firebasedatabase.app"
    })
except Exception as e:
    print(f"⚠️ Firebase xatosi: {str(e)}")

ref = db.reference("phone_verifications")

# =========================
# BOT SETUP
# =========================
bot = Bot(token=TOKEN)
dp = Dispatcher()

# =========================
# FIREBASE TEST
# =========================
def test_firebase():
    """Firebase ulanishini test qilish"""
    try:
        print("\n" + "="*50)
        print("🧪 FIREBASE TEST BOSHLANDI")
        print("="*50)
        
        test_data = ref.get()
        print(f"✅ Firebase ulanildi!")
        print(f"📋 phone_verifications data: {test_data.val()}")
        
        if test_data.val():
            print(f"\n✅ Ma'lumotlar bazada mavjud:")
            for phone, data in test_data.val().items():
                print(f"   📞 {phone}: {data}")
        else:
            print(f"\n⚠️ phone_verifications collection bo'sh!")
            
        print("="*50 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Firebase xatosi: {str(e)}")
        print("❌ Tekshiringlar:")
        print("   1. FIREBASE_CREDENTIALS_JSON yoki FIREBASE_CREDENTIAL_PATH to'g'rimi?")
        print("   2. Firebase URL to'g'rimi?")
        print("   3. Database rules to'g'rimi?")
        print("="*50 + "\n")
        return False

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
    try:
        phone = message.contact.phone_number.replace("+", "")
        print(f"📞 Telefon olindi: {phone}")

        user = ref.child(phone).get()
        if user.val() is None:
            print(f"❌ Raqam bazada yo'q: {phone}")
            await message.answer(f"❌ Ushbu telefon raqami topilmadi.\n\n📞 Izlangan raqam: {phone}")
            return

        user_data = user.val()
        print(f"📋 User data: {user_data}")
        
        if "code" not in user_data:
            print(f"❌ 'code' field'i yo'q")
            await message.answer("❌ Tasdiqlash kodi topilmadi.")
            return

        code = user_data.get("code")
        print(f"✅ Kod topildi: {code}")
        
        ref.child(phone).update({"verified": True})
        print(f"✅ Verified: {phone}")

        await message.answer(f"✅ Tasdiqlash kodi:\n\n🔑 {code}")
        
    except Exception as e:
        print(f"⚠️ Xato: {str(e)}")
        await message.answer(f"⚠️ Xato yuz berdi:\n{str(e)}")

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
        print(f"❌ Webhook xatosi: {e}")
        return "error", 500

# =========================
# HEALTH CHECK
# =========================
@app.route("/", methods=["GET"])
def health():
    return "🤖 Bot ishlab turibdi!", 200

# =========================
# WEBHOOK REGISTRATION
# =========================
async def register_webhook():
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        print("⚠️ WEBHOOK_URL o'zgaruvchisi topilmadi")
        return
    
    try:
        await bot.set_webhook_url(webhook_url)
        print(f"✅ Webhook ro'yxatdan o'tkazildi: {webhook_url}")
    except Exception as e:
        print(f"⚠️ Webhook ro'yxatlash xatosi: {e}")

# =========================
# APP RUN
# =========================
if __name__ == "__main__":
    # Firebase testini ishga tushirish
    test_firebase()
    
    # Webhook ro'yxatdan o'tkazish
    asyncio.run(register_webhook())
    
    port = int(os.getenv("PORT", 5000))
    print(f"✅ Bot ishga tushdi: @{os.getenv('TELEGRAM_TOKEN', 'unknown')[:20]}...")
    print(f"🚀 Web server {port}-portda ishga tushmoqda...")
    
    app.run(host="0.0.0.0", port=port, debug=False)
