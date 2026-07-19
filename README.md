# Telegram Bot - Render Web Service Deploy

Bu bot **Web Service** sifatida Render-da ishlab turadi (24/7, keep-alive kerak emas).

## ⚠️ Muhim Xavfsizlik Eslatmalari

- **Telegram bot tokenini aslo hardcoded qilmang** - faqat environment variables ishlatish kerak
- **serviceAccountKey.json fayli repositoryga kiritilmasin** - uning o'rniga `FIREBASE_CREDENTIALS_JSON` yoki `FIREBASE_CREDENTIAL_PATH` o'zgaruvchilaridan foydalaning
- Har qanday token yoki kalit public bo'lsa, ularni darhol revoke/rotate qiling

## Architecture

```
User sends message to Telegram Bot
         ↓
Telegram sends webhook request to bot URL
         ↓
Flask receives POST request at /webhook
         ↓
Bot handler processes message
         ↓
Firebase queries phone verification data
         ↓
Bot sends response back to user
```

## How to run (local)

1. `.env` faylini yarating va quyidagilarni qo'shing:

```
TELEGRAM_TOKEN=YOUR_BOT_TOKEN
FIREBASE_DATABASE_URL=https://abituriyent-16e96-default-rtdb.europe-west1.firebasedatabase.app
FIREBASE_CREDENTIALS_JSON={...}
WEBHOOK_URL=http://localhost:5000/webhook
PORT=5000
```

2. Dependencies o'rnatib chiqish va ishga tushirish:

```bash
pip install -r requirements.txt
python main.py
```

## Deploy on Render (Web Service)

### 1. Render Dashboard-da yangi Web Service yaratish

- **Name:** abituriyernt-bot
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`
- **Plan:** Free

### 2. Environment Variables o'rnatish

Render dashboard-da quyidagi env o'zgaruvchilarini qo'shing:

```
TELEGRAM_TOKEN=your_bot_token_here
FIREBASE_DATABASE_URL=https://abituriyent-16e96-default-rtdb.europe-west1.firebasedatabase.app
FIREBASE_CREDENTIALS_JSON={...}
WEBHOOK_URL=https://abituriyernt-bot.onrender.com/webhook
PORT=5000
```

**FIREBASE_CREDENTIALS_JSON qanday qo'shish:**
1. serviceAccountKey.json faylini text editor-da oching
2. Butun JSON ni ko'chiring
3. Render dashboard-da paste qiling (multiline qabul qilinadi)

**WEBHOOK_URL qanday olish:**
- Render app deploy qilingandan so'ng, `https://<app-name>.onrender.com` ko'rinishida URL olasiz
- Webhook URL: `https://<app-name>.onrender.com/webhook`

### 3. Deploy

Push qiling GitHub-ga va Render avtomatik deploy qiladi ✅

## Struktura

```
.
├── main.py              Web service entry point (Flask + aiogram webhook)
├── requirements.txt     Python dependencies (Flask qo'shildi)
├── Procfile             Web service deployment config
├── runtime.txt          Python versiyasi
├── .gitignore           Sensitive files excludes
├── .env.example         Environment variables example
└── README.md            Bu fayl
```

## Features

✅ Telegram bot /start komandasiga javob beradi
✅ Foydalanuvchi telefon raqamini yuboradi
✅ Firebase Realtime Database-dan telefon ma'lumotlarini qidiradi
✅ Tasdiqlash kodi olmaganlarni qayta-qayta ko'rsatadi
✅ User verified deb belgilash
✅ **24/7 Web Service sifatida ishlab turadi** (Render free plan-da)
✅ Webhook orqali Telegram-dan message qabul qiladi

## Endpoints

- `GET /` - Health check (bot ishlab turibdimi?)
- `POST /webhook` - Telegram webhook endpoint (faqat Telegram yuboradi)

## Troubleshooting

### Firebase ulanish xatosi
- `FIREBASE_CREDENTIALS_JSON` yoki `FIREBASE_CREDENTIAL_PATH` to'g'ri qilib ko'rining
- JSON valid ekanligini tekshiring
- Firebase Realtime Database rules-larini tekshiring

### Bot salomdimadi
- `TELEGRAM_TOKEN` to'g'rimi tekshiring
- Token active va revoke qilinmagan ekanligini tekshiring

### Webhook registratsiyasi ishlamadi
- `WEBHOOK_URL` to'g'rimi tekshiring (https bilan bo'lishi kerak)
- Render app fully deploy bo'linganni kutish kerak

### Render logs-larida xatolar
- Render dashboard-da "Logs" tab-da xatolarni ko'ring
- Flask port 5000-da ishlab turibdimi?
- Environment variables to'liq qilib ko'ring

## Foydalanish

1. Telegram-da @abituriyernt-bot-ga /start yuboringiz
2. "📱 Telefon raqamni yuborish" tugmasini boshing
3. Telefon raqamingizni yuboring
4. Bot Firebase-dan tasdiqlash kodi oladi va ko'rsatadi
5. User verified deb belgilanadi ✅
