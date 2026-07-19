import asyncio
import os
import json
import tempfile
import datetime

import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# Load .env for local testing (Render will use ENV vars set in dashboard)
load_dotenv()

# =========================
# ENV / CONFIG
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise SystemExit("TELEGRAM_TOKEN environment variable required")

FIREBASE_DATABASE_URL = os.getenv(
    "FIREBASE_DATABASE_URL",
    "https://abituriyent-16e96-default-rtdb.europe-west1.firebasedatabase.app"
)

# Optional: provide service account JSON directly as env (multiline allowed)
FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")
FIREBASE_CREDENTIAL_PATH = os.getenv("FIREBASE_CREDENTIAL_PATH")  # optional path on server

# GitHub push config (optional)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # format: owner/repo
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")


# =========================
# FIREBASE INIT (flexible)
# =========================
firebase_app = None
_temp_cred_file = None

def _init_firebase():
    global firebase_app, _temp_cred_file
    try:
        if FIREBASE_CREDENTIALS_JSON:
            try:
                cred_dict = json.loads(FIREBASE_CREDENTIALS_JSON)
            except Exception:
                # In case env contains a JSON string with newlines, try to load directly
                cred_dict = json.loads(FIREBASE_CREDENTIALS_JSON.replace("\\n", "\n"))
            # write to temp file because credentials.Certificate works well with a file
            tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
            tmp.write(json.dumps(cred_dict))
            tmp.flush()
            _temp_cred_file = tmp.name
            cred = credentials.Certificate(_temp_cred_file)
            firebase_app = firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DATABASE_URL})
            return True

        if FIREBASE_CREDENTIAL_PATH and os.path.exists(FIREBASE_CREDENTIAL_PATH):
            cred = credentials.Certificate(FIREBASE_CREDENTIAL_PATH)
            firebase_app = firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DATABASE_URL})
            return True

        # fallback: local file inside repo (not recommended for production)
        local_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
        if os.path.exists(local_path):
            cred = credentials.Certificate(local_path)
            firebase_app = firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DATABASE_URL})
            return True

        print("⚠️ Firebase credential not found. Set FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIAL_PATH.")
        return False

    except ValueError:
        # already initialized
        firebase_app = firebase_admin.get_app()
        return True
    except Exception as e:
        print("❌ Firebase init error:", str(e))
        return False

firebase_ready = _init_firebase()
ref = db.reference("phone_verifications") if firebase_ready else None


# =========================
# GITHUB PUSH (optional, safe)
# =========================
def push_to_github(commit_message="Auto-update from bot"):
    """Optional: append an entry into verifications log file in the GitHub repo using API.
    This avoids running `git` and embedding tokens in remote URLs.
    Requires GITHUB_TOKEN and GITHUB_REPO env vars.
    """
    if not (GITHUB_TOKEN and GITHUB_REPO):
        print("ℹ️ GITHUB_TOKEN or GITHUB_REPO not set — skipping GitHub push")
        return False

    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        log_path = "verifications.txt"
        entry = f"{datetime.datetime.utcnow().isoformat()} - {commit_message}\n"

        try:
            contents = repo.get_contents(log_path, ref=GITHUB_BRANCH)
            existing = contents.decoded_content.decode()
            new_content = existing + entry
            repo.update_file(log_path, commit_message, new_content, contents.sha, branch=GITHUB_BRANCH)
        except Exception:
            # file doesn't exist — create
            repo.create_file(log_path, commit_message, entry, branch=GITHUB_BRANCH)

        print("✅ Pushed verification entry to GitHub")
        return True
    except Exception as e:
        print("❌ GitHub push error:", str(e))
        return False


# =========================
# FIREBASE TEST (safe)
# =========================
def test_firebase():
    """Test firebase connection and print a summary (no .val() — use Python dict)."""
    if not ref:
        print("⚠️ Firebase not initialized; skipping test_firebase()")
        return False

    try:
        print("\n" + "=" * 50)
        print("🧪 FIREBASE TEST BOSHLANDI")
        print("=" * 50)

        test_data = ref.get()
        print("✅ Firebase ulanildi!")
        print(f"📋 phone_verifications data: {test_data}")

        if test_data:
            print("\n✅ Ma'lumotlar bazada mavjud:")
            for phone, data in test_data.items():
                print(f"   📞 {phone}: {data}")
        else:
            print("\n⚠️ phone_verifications collection bo'sh!")

        print("=" * 50 + "\n")
        return True
    except Exception as e:
        print("\n❌ Firebase xatosi:", str(e))
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
    if not ref:
        await message.answer("❌ Xatolik: Firebase ulanmadi. Admin bilan bog'laning.")
        return

    try:
        phone = message.contact.phone_number
        print(f"📞 Telefon olindi: {phone}")

        # + ni olib tashlaymiz
        phone = phone.replace("+", "").strip()
        print(f"📞 Formatlandirilgan raqam: {phone}")

        # Firebase'dan qidirish
        user = ref.child(phone).get()  # dict or None
        print(f"🔍 Firebase so'rovi: {user if user else 'Topilmadi'}")

        if not user:
            await message.answer(
                "❌ Ushbu telefon raqami ilovada topilmadi.\n\n"
                f"📞 Izlangan raqam: {phone}\n"
                "Firebase'da ushbu raqam mavjud emasligini tekshiring."
            )
            return

        user_data = user  # dict
        print(f"📋 User data keys: {list(user_data.keys())}")

        # Code mavjud ekanligini tekshirish
        if "code" not in user_data:
            await message.answer(
                "❌ Tasdiqlash kodi topilmadi.\n"
                "Firebase'da 'code' field'i mavjud emas."
            )
            return

        code = user_data.get("code")
        # Verifikatsiyani yangilash
        ref.child(phone).update({
            "verified": True
        })
        print(f"✅ Verified: {phone}")

        await message.answer(
            f"✅ Tasdiqlash kodi:\n\n"
            f"🔑 {code}"
        )

        # GitHub'ga push qilish (optional)
        push_to_github(f"Telefon verify: {phone}")

    except Exception as e:
        print("⚠️ Xato:", str(e))
        await message.answer("⚠️ Xato yuz berdi, adminga murojaat qiling.")


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
    try:
        asyncio.run(main())
    finally:
        # clean up temp credential file if created
        try:
            if _temp_cred_file and os.path.exists(_temp_cred_file):
                os.remove(_temp_cred_file)
        except Exception:
            pass
