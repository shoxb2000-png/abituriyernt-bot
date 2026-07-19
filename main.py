import asyncio
import os
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv
from git import Repo
from github import Github

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# Load environment variables
load_dotenv()

# =========================
# BOT TOKEN
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN", "8900139451:AAHMLIYUi789MtY-Eh7TvEcr4QjSs3d4QRw")

# =========================
# FIREBASE
# =========================
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": "https://abituriyent-16e96-default-rtdb.europe-west1.firebasedatabase.app"
        }
    )
except ValueError:
    # Agar allaqachon initsializatsiya qilingan bo'lsa
    pass

ref = db.reference("phone_verifications")

# =========================
# GITHUB PUSH FUNCTION
# =========================
def push_to_github(commit_message="Auto-update from bot"):
    """GitHub repositoryga kod yuklash funksiyasi"""
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        github_repo = os.getenv("GITHUB_REPO")
        github_branch = os.getenv("GITHUB_BRANCH", "main")
        
        if not github_token or not github_repo:
            print("⚠️ GitHub credentials topilmadi")
            return False
        
        # Local git repo
        repo = Repo(".")
        
        # Barcha o'zgarishlarni stage qilish
        repo.git.add(A=True)
        
        # Commit qilish
        repo.index.commit(commit_message)
        
        # Push qilish
        origin = repo.remote("origin")
        origin.push(github_branch)
        
        print(f"✅ GitHub'ga push qilindi: {commit_message}")
        return True
        
    except Exception as e:
        print(f"❌ GitHub push xatosi: {str(e)}")
        return False

# =========================
# FIREBASE TEST
# =========================
def test_firebase():
    """Firebase ulanishini test qilish"""
    try:
        print("\n" + "="*50)
        print("🧪 FIREBASE TEST BOSHLANDI")
        print("="*50)
        
        # Database mavjudligini tekshirish
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
        print("   1. serviceAccountKey.json fayli mavjudmi?")
        print("   2. Firebase URL to'g'rimi?")
        print("   3. Database rules to'g'rimi?")
        print("="*50 + "\n")
        return False

# =========================
# BOT
# =========================
bot = Bot(token=TOKEN)
dp = Dispatcher()


# =========================
# START
# =========================
@dp.message(CommandStart())
async def start(message: Message):

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 Telefon raqamni yuborish",
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Ro'yxatdan o'tishni davom ettirish uchun telefon raqamingizni yuboring.",
        reply_markup=keyboard
    )


# =========================
# CONTACT
# =========================
@dp.message(F.contact)
async def contact_handler(message: Message):
    try:
        phone = message.contact.phone_number
        print(f"📞 Telefon olindi: {phone}")

        # + ni olib tashlaymiz
        phone = phone.replace("+", "")
        print(f"📞 Formatlandirilgan raqam: {phone}")

        # Firebase'dan qidirish
        user = ref.child(phone).get()
        print(f"🔍 Firebase so'rovi: {user.val() if user.val() else 'Topilmadi'}")

        if user.val() is None:
            print(f"❌ Raqam bazada yo'q: {phone}")
            await message.answer(
                "❌ Ushbu telefon raqami ilovada topilmadi.\n\n"
                f"📞 Izlangan raqam: {phone}\n"
                "Firebase'da ushbu raqam mavjud emasligini tekshiring."
            )
            return

        user_data = user.val()
        print(f"📋 User data: {user_data}")

        # Code mavjud ekanligini tekshirish
        if "code" not in user_data:
            print(f"❌ 'code' field'i yo'q")
            await message.answer(
                "❌ Tasdiqlash kodi topilmadi.\n"
                "Firebase'da 'code' field'i mavjud emas."
            )
            return

        code = user_data.get("code")
        print(f"✅ Kod topildi: {code}")

        # Verifikatsiyani yangilash
        ref.child(phone).update({
            "verified": True
        })
        print(f"✅ Verified: {phone}")

        await message.answer(
            f"✅ Tasdiqlash kodi:\n\n"
            f"🔑 {code}"
        )
        
        # GitHub'ga push qilish
        push_to_github(f"Telefon verify: {phone}")
        
    except Exception as e:
        print(f"⚠️ Xato: {str(e)}")
        await message.answer(
            f"⚠️ Xato yuz berdi:\n{str(e)}"
        )


async def main():
    # Firebase testini ishga tushirish
    test_firebase()
    
    me = await bot.get_me()
    print(f"✅ Bot ishga tushdi: @{me.username}")
    print(f"🤖 Bot Polling rejimida...\n")

    await dp.start_polling(
        bot,
        polling_timeout=10
    )
if __name__ == "__main__":
    asyncio.run(main())
