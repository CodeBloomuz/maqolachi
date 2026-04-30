# maqolachi

# 📚 Maqola Yozdirish Telegram Boti

## 🚀 O'rnatish va Ishga Tushirish

### 1. Bot Token olish
1. Telegramda @BotFather ga o'ting
2. /newbot deb yozing
3. Bot nomini kiriting (masalan: MaqolaYozdirish)
4. Username kiriting (masalan: maqola_yozdirish_bot)
5. Token olasiz — uni saqlang

### 2. Admin ID olish
1. Telegramda @userinfobot ga o'ting
2. /start deb yozing
3. Sizning ID raqamingiz ko'rinadi — uni saqlang

### 3. bot.py ni sozlash
bot.py faylini oching va quyidagilarni o'zgartiring:
```
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # Bot tokeningizni yozing
ADMIN_ID = 123456789                # Admin ID raqamingizni yozing
```

### 4. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 5. Botni ishga tushirish
```bash
python bot.py
```

---

## 🛠 Bot qanday ishlaydi

### Foydalanuvchi uchun:
1. /start → Menyu ko'rinadi
2. "📝 Maqola yozdirish" yoki "🔬 Scopus maqola" tugmasini bosadi
3. Ma'lumotlarni bosqichma-bosqich kiritadi
4. Ariza tasdiqlangach — 50% to'lov haqida xabar keladi
5. To'lov qilib, chek rasmini yuboradi
6. Admin tasdiqlaydi → "Maqolangiz ish jarayonida" deb xabar keladi
7. Maqola tayyor bo'lgach → 50% yakuniy to'lov so'raladi
8. Yakuniy to'lov tasdiqlangach → maqola yuboriladi

### Admin uchun:
- Yangi ariza kelganda — xabar oladi
- Chek kelganda — ✅ Tasdiqlash / ❌ Rad etish tugmalari chiqadi
- `/ready USER_ID` — Foydalanuvchiga "Maqola tayyor, 50% to'lang" xabarini yuboradi
- `/send_article USER_ID` — Maqolani yuborish rejimiga o'tadi, keyin fayl yuboriladi

---

## 📋 Admin buyruqlari

| Buyruq | Tavsifi |
|--------|---------|
| /admin_help | Barcha admin buyruqlarini ko'rish |
| /ready 123456 | Foydalanuvchiga maqola tayyor deb xabar berish |
| /send_article 123456 | Maqolani foydalanuvchiga yuborish |

---

## 🔄 To'liq jarayon

```
Foydalanuvchi ariza topshiradi
        ↓
Admin arizani ko'radi
        ↓
Foydalanuvchi 50% to'laydi + chek yuboradi
        ↓
Admin chekni tasdiqlaydi
        ↓
"Maqolangiz ish jarayonida" (30 daqiqa - 1 soat)
        ↓
Admin /ready USER_ID yuboradi
        ↓
Foydalanuvchi 50% yakuniy to'lov qiladi + chek yuboradi
        ↓
Admin chekni tasdiqlaydi
        ↓
Admin /send_article USER_ID → fayl yuboradi
        ↓
Foydalanuvchi maqolani oladi ✅
```

---

## ⚠️ Muhim eslatmalar

- Bot `python bot.py` to'xtaganda ishlamaydi
- Uzluksiz ishlashi uchun serverga (VPS) yoki [Railway.app](https://railway.app), [Render.com](https://render.com) ga joylang
- Foydalanuvchi ID larini ma'lumotlar bazasiga saqlash uchun SQLite qo'shish mumkin

---

## 📞 Yordam

Muammo bo'lsa, bot kodini ishlab chiquvchi bilan bog'laning.
