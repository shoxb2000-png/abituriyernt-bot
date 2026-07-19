# Telegram Bot - Render Deploy

## � Firebase Data Structure

Bot ishlamasi uchun Firebase'da quyidagi format bo'lishi kerak:

```json
{
  "phone_verifications": {
    "998901234567": {
      "code": "12345",
      "verified": false,
      "name": "Ali"
    },
    "998987654321": {
      "code": "54321",
      "verified": true,
      "name": "Vali"
    }
  }
}
```

**Talab qilinadigan field'lar:**
- `phone_verifications/{phone}/code` - Tasdiqlash kodi (KERAK) ⭐
- `phone_verifications/{phone}/verified` - Holati (optional)
- `phone_verifications/{phone}/name` - Ism (optional)

## 🧪 Lokal Testdan O'tkazish

### 1. Firebase'da ma'lumot qo'shish
Firebase Console → phone_verifications → [+] Add data
```json
{
  "998901234567": {
    "code": "12345",
    "verified": false
  }
}
```

### 2. `.env` faylini to'ldirish
```
TELEGRAM_TOKEN=YOUR_BOT_TOKEN
```

### 3. Bot'ni lokal'da ishga tushirish
```bash
pip install -r requirements.txt
python main.py
```

**Natija:**
```
==================================================
🧪 FIREBASE TEST BOSHLANDI
==================================================
✅ Firebase ulanildi!
📋 phone_verifications data: {...}

✅ Ma'lumotlar bazada mavjud:
   📞 998901234567: {'code': '12345', 'verified': False}
==================================================

✅ Bot ishga tushdi: @YourBotName
🤖 Bot Polling rejimida...
```

### 4. Bot'ni test qilish
- Bot'ga `/start` yuboring
- "📱 Telefon raqamni yuborish" tugmasini bosing
- **Natija:**
  - ✅ Agar raqam Firebase'da bo'lsa → Kodni yuboradi
  - ❌ Agar raqam bazada bo'lmasa → Xato xabari

## 📝 GitHub'ga yuklashni o'rgatish

### 1. GitHub'da yangi repository yaratish
1. [github.com](https://github.com) saytiga kiring
2. "+" → "New repository" bosing
3. Nom bering: `telegram-bot` (yoki boshqa)
4. Public tanlang (Render yuklashi uchun)
5. Create repository bosing

### 2. Kompyuteringizda git setup
```bash
cd /path/to/Telegram_bot

# Git initsializatsiya
git init
git config user.name "Your Name"
git config user.email "your-email@example.com"

# Remote repositoryni qo'shish
git remote add origin https://github.com/YOUR_USERNAME/telegram-bot.git

# Barcha fayllarni qo'shish
git add .

# Commit qilish
git commit -m "Initial commit - Telegram bot"

# GitHub'ga push qilish
git push -u origin main
```

### 3. GitHub Token yaratish (Bot uchun)
1. GitHub → Settings → Developer settings → Personal access tokens
2. "Generate new token" → "Generate new token (classic)"
3. Scope: `repo` (full control of private repositories)
4. Token'ni copy qiling va `.env` faylida qo'shing:
```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxx
GITHUB_REPO=YOUR_USERNAME/telegram-bot
GITHUB_BRANCH=main
```

### 4. Render'da deploy qilish
- [render.com](https://render.com) ga kiring
- GitHub bilan login qiling
- "New +" → "Web Service"
- Repositoriyangizni ulang

### 5. Render Settings
- **Name**: telegram-bot
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Instance Type**: Free

### 6. Environment Variables (Render'da qo'shing)
```
TELEGRAM_TOKEN=8900139451:AAHMLIYUi789MtY-Eh7TvEcr4QjSs3d4QRw
FIREBASE_DATABASE_URL=https://abituriyent-16e96-default-rtdb.europe-west1.firebasedatabase.app
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxx
GITHUB_REPO=YOUR_USERNAME/telegram-bot
GITHUB_BRANCH=main
```

### 7. Deploy
- Deploy tugmasini bosing
- Bot 3-5 daqiqaning ichida ishga tushadi
- **Har safar verifikatsiya bo'lganda, bot avtomatik GitHub'ga push qiladi!** ✅

## 🤖 Bot Vazifasi
- Telefon raqamini oladi
- Firebase databasedan tekshiradi
- Tasdiqlash kodini yuboradi
- Verifikatsiyani GitHub'ga saqlaydi

## 📦 Kerakli fayllar
- `main.py` - Bot kodi
- `firebase.py` - Firebase konfiguratsiyasi
- `requirements.txt` - Dependencies
- `.env` - Maxfiy kalitlar (Git'ga ko'rinmaydi)
- `serviceAccountKey.json` - Firebase key (Git'ga ko'rinmaydi)


