# Telegram Bot - Render Deploy (cleaned)

Bu branch (clean-rebuild) xavfsiz va ishlaydigan variant uchun tayyorlandi.

Muhim:
- serviceAccountKey.json fayl repositoryga kiritilmasin; uning o‘rniga FIREBASE_CREDENTIALS_JSON yoki FIREBASE_CREDENTIAL_PATH o‘zgaruvchilaridan foydalaning.
- Har qanday token yoki kalit public bo‘lsa, ularni darhol revoke/rotate qiling.

How to run (local):

1. .env faylini yarating va quyidagilarni qo‘shing:

```
TELEGRAM_TOKEN=YOUR_BOT_TOKEN
FIREBASE_DATABASE_URL=https://abituriyent-16e96-default-rtdb.europe-west1.firebasedatabase.app
# Option 1: paste full JSON (multiline) - recommended for Render secret
FIREBASE_CREDENTIALS_JSON={...}
# OR Option 2: provide path to credentials on server
FIREBASE_CREDENTIAL_PATH=/path/to/serviceAccountKey.json
```

2. Install deps and run:

```
pip install -r requirements.txt
python Telegram_bot/main.py
```

Deploy notes for Render:
- Set runtime.txt to python-3.11.16 (provided)
- Build Command: pip install -r requirements.txt
- Start Command: python Telegram_bot/main.py
- Add ENV vars in Render dashboard (TELEGRAM_TOKEN, FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIAL_PATH)

