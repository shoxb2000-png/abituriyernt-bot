# Telegram Bot - Render Deploy (cleaned)

Bu branch (clean-rebuild) xavfsiz va ishlaydigan variant uchun tayyorlandi.

## ⚠️ Muhim Xavfsizlik Eslatmalari

- **Telegram bot tokenini aslo hardcoded qilmang** - faqat environment variables ishlatish kerak
- **serviceAccountKey.json fayli repositoryga kiritilmasin** - uning o'rniga `FIREBASE_CREDENTIALS_JSON` yoki `FIREBASE_CREDENTIAL_PATH` o'zgaruvchilaridan foydalaning
- Har qanday token yoki kalit public bo'lsa, ularni darhol revoke/rotate qiling

## How to run (local)

1. `.env` faylini yarating va quyidagilarni qo'shing:

```
TELEGRAM_TOKEN=YOUR_BOT_TOKEN
FIREBASE_DATABASE_URL=https://abituriyent-16e96-default-rtdb.europe-west1.firebasedatabase.app
# Quyidagilardan birini tanlang:
# Variant 1: JSON stringni to'liq qo'shing (tavsiyalangan - Render-da ishlatish uchun)
FIREBASE_CREDENTIALS_JSON={...}
# YOKI Variant 2: Fayl yo'lini ko'rsating (local development uchun)
FIREBASE_CREDENTIAL_PATH=/path/to/serviceAccountKey.json
```

2. Dependencies o'rnatib chiqish va ishga tushirish:

```bash
pip install -r requirements.txt
python main.py
```

## Deploy on Render

### 1. Environment Variables o'rnatish

Render dashboard-da quyidagi env o'zgaruvchilarini qo'shing:

```
TELEGRAM_TOKEN=your_bot_token_here
FIREBASE_DATABASE_URL=https://abituriyent-16e96-default-rtdb.europe-west1.firebasedatabase.app
FIREBASE_CREDENTIALS_JSON={...}  # serviceAccountKey.json ni JSON string sifatida qo'shing
```

**FIREBASE_CREDENTIALS_JSON qanday qo'shish:**
1. serviceAccountKey.json faylini text editor-da oching
2. Butun JSON ni ko'chiring
3. Render dashboard-da paste qiling (multiline qabul qilinadi)

### 2. Build va Start Commands

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`

### 3. Runtime

- Python version: `3.11.16` (runtime.txt-da belgilangan)

## Struktura

```
.
├── main.py              Bot entry point (async Telegram bot)
├── requirements.txt     Python dependencies
├── runtime.txt          Python versiyasi
├── Procfile             Render deployment config
├── .gitignore           Sensitive files excludes
└── README.md            Bu fayl
```

## Features

✅ Telegram bot user /start komandasiga javob beradi
✅ Foydalanuvchi telefon raqamini yuboradi
✅ Firebase Realtime Database-dan telefon ma'lumotlarini qidiradi
✅ Tasdiqlash kodi olmaganlarni qayta-qayta ko'rsatadi
✅ User verified deb belgilash
✅ GitHub'ga avtomatik push (ixtiyoriy)

## Troubleshooting

### Firebase ulanish xatosi
- `FIREBASE_CREDENTIALS_JSON` yoki `FIREBASE_CREDENTIAL_PATH` to'g'ri qilib ko'rining
- JSON valid ekanligini tekshiring
- Firebase Realtime Database rules-larini tekshiring

### Bot salomdimadi
- `TELEGRAM_TOKEN` to'g'rimi tekshiring
- Token active va revoke qilinmagan ekanligini tekshiring

### Render logs-larida xatolar
- `Procfile` to'g'rimi (main.py yo'li)
- Barcha requirements.txt-da mavjud ekanligini tekshiring
