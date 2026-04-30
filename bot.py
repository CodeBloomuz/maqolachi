import logging
import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)

# === SOZLAMALAR ===
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 123456789  # Admin Telegram ID sini kiriting

# === HOLATLAR ===
# Maqola yozdirish uchun
(
    ARTICLE_FULL_NAME, ARTICLE_UNI, ARTICLE_FACULTY, ARTICLE_DIRECTION,
    ARTICLE_COURSE, ARTICLE_SUPERVISOR, ARTICLE_TITLE, ARTICLE_LANG,
    ARTICLE_CONTACT, ARTICLE_EMAIL, ARTICLE_CONFIRM,
    ARTICLE_WAIT_CHECK, ARTICLE_WAIT_FINAL
) = range(13)

# Scopus maqola uchun
(
    SCOPUS_NAME, SCOPUS_UNI, SCOPUS_FACULTY, SCOPUS_CITY,
    SCOPUS_EMAIL, SCOPUS_ORCID, SCOPUS_TITLE, SCOPUS_LANG,
    SCOPUS_CONFIRM, SCOPUS_WAIT_CHECK, SCOPUS_WAIT_FINAL
) = range(13, 24)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Foydalanuvchi ma'lumotlari vaqtincha saqlanadi
user_data_store = {}
pending_articles = {}  # {user_id: article_data}

# === ASOSIY MENYU ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Maqola yozdirish", callback_data="article")],
        [InlineKeyboardButton("🔬 Scopus maqola yozdirish", callback_data="scopus")],
        [InlineKeyboardButton("ℹ️ Biz haqimizda", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎓 *Maqola Yozish Xizmatiga Xush Kelibsiz!*\n\n"
        "Biz siz uchun sifatli ilmiy maqolalar yozamiz.\n"
        "Xizmat turini tanlang:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_text(
            "ℹ️ *Biz haqimizda*\n\n"
            "Biz professional ilmiy maqolalar yozish xizmati taqdim etamiz.\n"
            "• Maqola yozilish muddati: 30 daqiqadan 1 soatgacha\n"
            "• To'lov: 50% oldindan, 50% maqola tayyor bo'lgandan so'ng\n\n"
            "Savollar uchun: @admin_username",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")
            ]])
        )
    elif query.data == "back_main":
        keyboard = [
            [InlineKeyboardButton("📝 Maqola yozdirish", callback_data="article")],
            [InlineKeyboardButton("🔬 Scopus maqola yozdirish", callback_data="scopus")],
            [InlineKeyboardButton("ℹ️ Biz haqimizda", callback_data="about")],
        ]
        await query.edit_message_text(
            "🎓 *Maqola Yozish Xizmatiga Xush Kelibsiz!*\n\n"
            "Xizmat turini tanlang:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ================================================================
# === MAQOLA YOZDIRISH ===
# ================================================================

async def article_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    context.user_data['type'] = 'article'
    await query.edit_message_text(
        "📝 *Maqola Yozdirish Arizasi*\n\n"
        "Ariza to'ldirish bosqichlarini boshlayapmiz.\n\n"
        "👤 *F.I.SH* ni kiriting:\n_(Familiya Ism Sharifingiz)_",
        parse_mode="Markdown"
    )
    return ARTICLE_FULL_NAME

async def article_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text(
        "🏛 *Universitet nomini* kiriting:"
    )
    return ARTICLE_UNI

async def article_uni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['university'] = update.message.text
    await update.message.reply_text(
        "🏢 *Fakultet nomini* kiriting:"
    )
    return ARTICLE_FACULTY

async def article_faculty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['faculty'] = update.message.text
    await update.message.reply_text(
        "📚 *Yo'nalishni* kiriting:"
    )
    return ARTICLE_DIRECTION

async def article_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['direction'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("1-kurs", callback_data="course_1"),
         InlineKeyboardButton("2-kurs", callback_data="course_2")],
        [InlineKeyboardButton("3-kurs", callback_data="course_3"),
         InlineKeyboardButton("4-kurs", callback_data="course_4")],
    ]
    await update.message.reply_text(
        "🎓 *Kursni* tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ARTICLE_COURSE

async def article_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['course'] = query.data.replace("course_", "") + "-kurs"
    await query.edit_message_text(
        "👨‍🏫 *Ilmiy rahbar* F.I.SH ni kiriting:"
    )
    return ARTICLE_SUPERVISOR

async def article_supervisor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['supervisor'] = update.message.text
    await update.message.reply_text(
        "📄 *Maqola nomi yoki mavzusini* kiriting:"
    )
    return ARTICLE_TITLE

async def article_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uzb")],
        [InlineKeyboardButton("🇷🇺 Rus", callback_data="lang_rus")],
        [InlineKeyboardButton("🇬🇧 Ingliz", callback_data="lang_eng")],
        [InlineKeyboardButton("🌐 Uchala tilda (UZB+RUS+ENG)", callback_data="lang_all")],
    ]
    await update.message.reply_text(
        "🌍 *Maqola tilini* tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ARTICLE_LANG

async def article_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_map = {
        "lang_uzb": "O'zbek tili",
        "lang_rus": "Rus tili",
        "lang_eng": "Ingliz tili",
        "lang_all": "O'zbek + Rus + Ingliz (3 tilda)"
    }
    context.user_data['language'] = lang_map.get(query.data, "Noaniq")
    keyboard = [
        [InlineKeyboardButton("📞 Kontakt ma'lumot kiritish", callback_data="contact_yes")],
        [InlineKeyboardButton("⏭ O'tkazib yuborish", callback_data="contact_no")],
    ]
    await query.edit_message_text(
        "📞 *Kontakt ma'lumotlar* (ixtiyoriy)\n\nTelefon raqam yoki Telegram username kiriting?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ARTICLE_CONTACT

async def article_contact_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "contact_yes":
        await query.edit_message_text("📞 Kontakt ma'lumotingizni kiriting:")
        return ARTICLE_CONTACT
    else:
        context.user_data['contact'] = "Ko'rsatilmagan"
        keyboard = [
            [InlineKeyboardButton("📧 Email kiritish", callback_data="email_yes")],
            [InlineKeyboardButton("⏭ O'tkazib yuborish", callback_data="email_no")],
        ]
        await query.edit_message_text(
            "📧 *Pochta manzili* (ixtiyoriy)\n\nEmail manzilingizni kiriting?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ARTICLE_EMAIL

async def article_contact_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("📧 Email kiritish", callback_data="email_yes")],
        [InlineKeyboardButton("⏭ O'tkazib yuborish", callback_data="email_no")],
    ]
    await update.message.reply_text(
        "📧 *Pochta manzili* (ixtiyoriy)\n\nEmail manzilingizni kiriting?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ARTICLE_EMAIL

async def article_email_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "email_yes":
        await query.edit_message_text("📧 Email manzilingizni kiriting:")
        return ARTICLE_EMAIL
    else:
        context.user_data['email'] = "Ko'rsatilmagan"
        return await show_article_confirm(update, context)

async def article_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    return await show_article_confirm_msg(update, context)

async def show_article_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    text = (
        "✅ *Ariza ma'lumotlari:*\n\n"
        f"👤 F.I.SH: `{d.get('full_name', '-')}`\n"
        f"🏛 Universitet: `{d.get('university', '-')}`\n"
        f"🏢 Fakultet: `{d.get('faculty', '-')}`\n"
        f"📚 Yo'nalish: `{d.get('direction', '-')}`\n"
        f"🎓 Kurs: `{d.get('course', '-')}`\n"
        f"👨‍🏫 Ilmiy rahbar: `{d.get('supervisor', '-')}`\n"
        f"📄 Mavzu: `{d.get('title', '-')}`\n"
        f"🌍 Til: `{d.get('language', '-')}`\n"
        f"📞 Kontakt: `{d.get('contact', 'Ko\'rsatilmagan')}`\n"
        f"📧 Email: `{d.get('email', 'Ko\'rsatilmagan')}`\n\n"
        "Ma'lumotlar to'g'rimi?"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data="article_confirm")],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="article_cancel")],
    ]
    query = update.callback_query
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return ARTICLE_CONFIRM

async def show_article_confirm_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    text = (
        "✅ *Ariza ma'lumotlari:*\n\n"
        f"👤 F.I.SH: `{d.get('full_name', '-')}`\n"
        f"🏛 Universitet: `{d.get('university', '-')}`\n"
        f"🏢 Fakultet: `{d.get('faculty', '-')}`\n"
        f"📚 Yo'nalish: `{d.get('direction', '-')}`\n"
        f"🎓 Kurs: `{d.get('course', '-')}`\n"
        f"👨‍🏫 Ilmiy rahbar: `{d.get('supervisor', '-')}`\n"
        f"📄 Mavzu: `{d.get('title', '-')}`\n"
        f"🌍 Til: `{d.get('language', '-')}`\n"
        f"📞 Kontakt: `{d.get('contact', 'Ko\'rsatilmagan')}`\n"
        f"📧 Email: `{d.get('email', 'Ko\'rsatilmagan')}`\n\n"
        "Ma'lumotlar to'g'rimi?"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data="article_confirm")],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="article_cancel")],
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return ARTICLE_CONFIRM

async def article_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "article_cancel":
        await query.edit_message_text("❌ Ariza bekor qilindi. /start ni bosing.")
        return ConversationHandler.END

    user = query.from_user
    d = context.user_data

    # Adminга хабар юбориш
    admin_text = (
        "🆕 *YANGI MAQOLA ARIZASI (Oddiy)*\n\n"
        f"👤 Foydalanuvchi: [{user.first_name}](tg://user?id={user.id})\n"
        f"🆔 ID: `{user.id}`\n"
        f"📱 Username: @{user.username or 'Yo\'q'}\n\n"
        f"👤 F.I.SH: `{d.get('full_name')}`\n"
        f"🏛 Universitet: `{d.get('university')}`\n"
        f"🏢 Fakultet: `{d.get('faculty')}`\n"
        f"📚 Yo'nalish: `{d.get('direction')}`\n"
        f"🎓 Kurs: `{d.get('course')}`\n"
        f"👨‍🏫 Ilmiy rahbar: `{d.get('supervisor')}`\n"
        f"📄 Mavzu: `{d.get('title')}`\n"
        f"🌍 Til: `{d.get('language')}`\n"
        f"📞 Kontakt: `{d.get('contact', 'Yo\'q')}`\n"
        f"📧 Email: `{d.get('email', 'Yo\'q')}`"
    )
    await context.bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")

    # Pending saqlaymiz
    pending_articles[user.id] = {
        'type': 'article',
        'data': dict(d),
        'status': 'waiting_check'
    }

    await query.edit_message_text(
        "✅ *Arizangiz qabul qilindi!*\n\n"
        "💳 *To'lov haqida:*\n"
        "Maqola yozilishini boshlash uchun oldindan *50% to'lovni* amalga oshiring.\n\n"
        "To'lov rekvizitlari admindan keladi.\n"
        "To'lov qilgandan so'ng chekni yuboring.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("💳 To'lov qildim, chekni yuboraman", callback_data="send_check_article")
        ]])
    )
    return ARTICLE_WAIT_CHECK

async def article_send_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📸 Iltimos, to'lov chekining *rasmini yoki skrinshot*ini yuboring:"
    )
    return ARTICLE_WAIT_CHECK

async def article_receive_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        caption = f"💳 Chek keldi!\n👤 [{user.first_name}](tg://user?id={user.id})\n🆔 ID: `{user.id}`\n📝 Tur: Maqola yozdirish"
        keyboard = [[
            InlineKeyboardButton("✅ Chekni tasdiqlash", callback_data=f"approve_check_{user.id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_check_{user.id}")
        ]]
        await context.bot.send_photo(
            ADMIN_ID, file_id,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text(
            "✅ Chek yuborildi!\n\n"
            "Admin tekshirgandan so'ng maqolangiz yozila boshlaydi.\n"
            "⏳ Natijani kuting..."
        )
    else:
        await update.message.reply_text("📸 Iltimos, rasm (chek) yuboring.")
        return ARTICLE_WAIT_CHECK

    return ARTICLE_WAIT_FINAL

# ================================================================
# === SCOPUS MAQOLA YOZDIRISH ===
# ================================================================

async def scopus_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    context.user_data['type'] = 'scopus'
    await query.edit_message_text(
        "🔬 *Scopus Maqola Yozdirish Arizasi*\n\n"
        "Muallif haqida ma'lumot to'ldiramiz.\n\n"
        "👤 *F.I.SH* (Author's Full Name) kiriting:",
        parse_mode="Markdown"
    )
    return SCOPUS_NAME

async def scopus_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text("🏛 *Universitet nomini* kiriting:", parse_mode="Markdown")
    return SCOPUS_UNI

async def scopus_uni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['university'] = update.message.text
    await update.message.reply_text("🏢 *Fakultet yoki bo'lim* nomini kiriting:", parse_mode="Markdown")
    return SCOPUS_FACULTY

async def scopus_faculty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['faculty'] = update.message.text
    await update.message.reply_text("🌆 *Shahar, Davlat* kiriting:\n_(Masalan: Toshkent, O'zbekiston)_", parse_mode="Markdown")
    return SCOPUS_CITY

async def scopus_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['city'] = update.message.text
    await update.message.reply_text("📧 *Email manzilingizni* kiriting:", parse_mode="Markdown")
    return SCOPUS_EMAIL

async def scopus_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("📝 ORCID ID kiritish", callback_data="orcid_yes")],
        [InlineKeyboardButton("⏭ ORCID ID yo'q", callback_data="orcid_no")],
    ]
    await update.message.reply_text(
        "🔑 *ORCID ID* bormi?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SCOPUS_ORCID

async def scopus_orcid_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "orcid_yes":
        await query.edit_message_text("🔑 ORCID ID ni kiriting:\n_(Masalan: 0000-0002-1234-5678)_")
        return SCOPUS_ORCID
    else:
        context.user_data['orcid'] = "Yo'q"
        await query.edit_message_text("📄 *Maqola nomi yoki mavzusini* kiriting:", parse_mode="Markdown")
        return SCOPUS_TITLE

async def scopus_orcid_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['orcid'] = update.message.text
    await update.message.reply_text("📄 *Maqola nomi yoki mavzusini* kiriting:", parse_mode="Markdown")
    return SCOPUS_TITLE

async def scopus_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="slang_uzb")],
        [InlineKeyboardButton("🇷🇺 Rus", callback_data="slang_rus")],
        [InlineKeyboardButton("🇬🇧 Ingliz", callback_data="slang_eng")],
        [InlineKeyboardButton("🌐 Uchala tilda", callback_data="slang_all")],
    ]
    await update.message.reply_text(
        "🌍 *Maqola tilini* tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SCOPUS_LANG

async def scopus_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_map = {
        "slang_uzb": "O'zbek tili",
        "slang_rus": "Rus tili",
        "slang_eng": "Ingliz tili",
        "slang_all": "O'zbek + Rus + Ingliz (3 tilda)"
    }
    context.user_data['language'] = lang_map.get(query.data, "Noaniq")

    d = context.user_data
    text = (
        "✅ *Scopus Ariza Ma'lumotlari:*\n\n"
        f"👤 F.I.SH: `{d.get('full_name', '-')}`\n"
        f"🏛 Universitet: `{d.get('university', '-')}`\n"
        f"🏢 Fakultet/Bo'lim: `{d.get('faculty', '-')}`\n"
        f"🌆 Shahar, Davlat: `{d.get('city', '-')}`\n"
        f"📧 Email: `{d.get('email', '-')}`\n"
        f"🔑 ORCID ID: `{d.get('orcid', 'Yo\'q')}`\n"
        f"📄 Mavzu: `{d.get('title', '-')}`\n"
        f"🌍 Til: `{d.get('language', '-')}`\n\n"
        "Ma'lumotlar to'g'rimi?"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data="scopus_confirm")],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="scopus_cancel")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return SCOPUS_CONFIRM

async def scopus_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "scopus_cancel":
        await query.edit_message_text("❌ Ariza bekor qilindi. /start ni bosing.")
        return ConversationHandler.END

    user = query.from_user
    d = context.user_data

    admin_text = (
        "🆕 *YANGI SCOPUS MAQOLA ARIZASI*\n\n"
        f"👤 Foydalanuvchi: [{user.first_name}](tg://user?id={user.id})\n"
        f"🆔 ID: `{user.id}`\n"
        f"📱 Username: @{user.username or 'Yo\'q'}\n\n"
        f"👤 F.I.SH: `{d.get('full_name')}`\n"
        f"🏛 Universitet: `{d.get('university')}`\n"
        f"🏢 Fakultet/Bo'lim: `{d.get('faculty')}`\n"
        f"🌆 Shahar, Davlat: `{d.get('city')}`\n"
        f"📧 Email: `{d.get('email')}`\n"
        f"🔑 ORCID ID: `{d.get('orcid', 'Yo\'q')}`\n"
        f"📄 Mavzu: `{d.get('title')}`\n"
        f"🌍 Til: `{d.get('language')}`"
    )
    await context.bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")

    pending_articles[user.id] = {
        'type': 'scopus',
        'data': dict(d),
        'status': 'waiting_check'
    }

    await query.edit_message_text(
        "✅ *Scopus arizangiz qabul qilindi!*\n\n"
        "💳 *To'lov haqida:*\n"
        "Maqola yozilishini boshlash uchun oldindan *50% to'lovni* amalga oshiring.\n\n"
        "To'lov rekvizitlari admindan keladi.\n"
        "To'lov qilgandan so'ng chekni yuboring.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("💳 To'lov qildim, chekni yuboraman", callback_data="send_check_scopus")
        ]])
    )
    return SCOPUS_WAIT_CHECK

async def scopus_send_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📸 Iltimos, to'lov chekining *rasmini* yuboring:")
    return SCOPUS_WAIT_CHECK

async def scopus_receive_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        caption = f"💳 Chek keldi!\n👤 [{user.first_name}](tg://user?id={user.id})\n🆔 ID: `{user.id}`\n🔬 Tur: Scopus maqola"
        keyboard = [[
            InlineKeyboardButton("✅ Chekni tasdiqlash", callback_data=f"approve_check_{user.id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_check_{user.id}")
        ]]
        await context.bot.send_photo(
            ADMIN_ID, file_id,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text(
            "✅ Chek yuborildi!\n\n"
            "Admin tekshirgandan so'ng maqolangiz yozila boshlaydi.\n"
            "⏳ Natijani kuting..."
        )
    else:
        await update.message.reply_text("📸 Iltimos, rasm (chek) yuboring.")
        return SCOPUS_WAIT_CHECK

    return SCOPUS_WAIT_FINAL

# ================================================================
# === ADMIN FUNKSIYALARI ===
# ================================================================

async def admin_check_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin chekni tasdiqlaydi"""
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Siz admin emassiz!", show_alert=True)
        return
    await query.answer()

    user_id = int(query.data.split("_")[-1])
    await context.bot.send_message(
        user_id,
        "✅ *To'lovingiz tasdiqlandi!*\n\n"
        "📝 Maqolangiz hozirda *ish jarayonida*.\n\n"
        "⏱ Maqola yozilishi *30 daqiqadan 1 soatgacha* davom etishi mumkin.\n"
        "Tayyor bo'lgach sizga xabar beriladi.",
        parse_mode="Markdown"
    )
    await query.edit_message_caption(
        caption=query.message.caption + "\n\n✅ *Chek tasdiqlandi*",
        parse_mode="Markdown"
    )

async def admin_check_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin chekni rad etadi"""
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Siz admin emassiz!", show_alert=True)
        return
    await query.answer()

    user_id = int(query.data.split("_")[-1])
    await context.bot.send_message(
        user_id,
        "❌ *To'lovingiz tasdiqlanmadi.*\n\n"
        "Iltimos, admin bilan bog'laning yoki qayta to'lov qiling.",
        parse_mode="Markdown"
    )
    await query.edit_message_caption(
        caption=query.message.caption + "\n\n❌ *Chek rad etildi*",
        parse_mode="Markdown"
    )

async def admin_article_ready(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin buyrug'i: /ready USER_ID
    Admin foydalanuvchiga maqola tayyor deb xabar beradi
    """
    if update.message.from_user.id != ADMIN_ID:
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "Foydalanish: /ready USER_ID\n"
            "Masalan: /ready 123456789"
        )
        return

    try:
        user_id = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri USER_ID")
        return

    await context.bot.send_message(
        user_id,
        "🎉 *Maqolangiz tayyor!*\n\n"
        "💳 Endi qolgan *50% to'lovni* amalga oshiring.\n"
        "To'lovdan so'ng chekni yuboring — maqola sizga yuboriladi.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("💳 50% to'lov qildim", callback_data=f"final_check_{user_id}")
        ]])
    )
    await update.message.reply_text(f"✅ {user_id} ga xabar yuborildi.")

async def admin_send_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin buyrug'i: /send_article USER_ID
    Admin maqolani foydalanuvchiga yuboradi (file yoki matn)
    """
    if update.message.from_user.id != ADMIN_ID:
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "Foydalanish: /send_article USER_ID\n"
            "Keyin maqola faylini yuboring."
        )
        return

    try:
        user_id = int(args[0])
        context.bot_data['pending_send_to'] = user_id
        await update.message.reply_text(
            f"✅ Keyingi yuboradigan fayl/matn {user_id} ga yuboriladi.\n"
            "Maqola faylini yuboring:"
        )
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri USER_ID")

async def admin_forward_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin maqola faylini yuborganda foydalanuvchiga yo'naltiradi"""
    if update.message.from_user.id != ADMIN_ID:
        return

    target_id = context.bot_data.get('pending_send_to')
    if not target_id:
        return

    try:
        if update.message.document:
            await context.bot.send_document(
                target_id,
                update.message.document.file_id,
                caption="📄 *Sizning maqolangiz tayyor!*\n\nHamkorlik uchun rahmat! 🎓",
                parse_mode="Markdown"
            )
        elif update.message.text and not update.message.text.startswith("/"):
            await context.bot.send_message(
                target_id,
                f"📄 *Sizning maqolangiz:*\n\n{update.message.text}",
                parse_mode="Markdown"
            )
        await update.message.reply_text(f"✅ Maqola {target_id} ga yuborildi!")
        context.bot_data.pop('pending_send_to', None)
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def final_check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi 50% yakuniy to'lov qildi deb chek yuboradi"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📸 Yakuniy to'lov chekining rasmini yuboring:")

async def final_check_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yakuniy chek admin ga yuboriladi"""
    user = update.message.from_user
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        caption = (
            f"💳 YAKUNIY CHEK!\n"
            f"👤 [{user.first_name}](tg://user?id={user.id})\n"
            f"🆔 ID: `{user.id}`\n"
            f"💰 50% yakuniy to'lov"
        )
        keyboard = [[
            InlineKeyboardButton("✅ Tasdiqlash va maqola yuborish", callback_data=f"final_approve_{user.id}")
        ]]
        await context.bot.send_photo(
            ADMIN_ID, file_id,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text(
            "✅ Yakuniy to'lov cheki yuborildi!\n"
            "Admin tasdiqlashi bilan maqolangiz keladi."
        )

async def final_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin yakuniy to'lovni tasdiqlaydi"""
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Siz admin emassiz!", show_alert=True)
        return
    await query.answer()

    user_id = int(query.data.split("_")[-1])
    context.bot_data['pending_send_to'] = user_id
    await query.edit_message_caption(
        caption=query.message.caption + "\n\n✅ *Tasdiqlandi. Maqolani yuboring!*",
        parse_mode="Markdown"
    )
    await context.bot.send_message(
        ADMIN_ID,
        f"📤 Endi /send_article {user_id} buyrug'ini bering va maqolani yuboring."
    )

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin barcha foydalanuvchilarga xabar yuboradi"""
    if update.message.from_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "📢 Broadcast funksiyasi (kelajakda qo'shiladi).\n"
        "Hozir /ready va /send_article buyruqlaridan foydalaning."
    )

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin buyruqlari"""
    if update.message.from_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "🔧 *Admin buyruqlari:*\n\n"
        "/ready USER_ID — Foydalanuvchiga maqola tayyor deb xabar berish\n"
        "/send_article USER_ID — Foydalanuvchiga maqola yuborish\n"
        "/admin_help — Ushbu yordam\n\n"
        "Chek kelganda tugmalardan foydalaning.",
        parse_mode="Markdown"
    )

# ================================================================
# === BOTNI ISHGA TUSHIRISH ===
# ================================================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Maqola yozdirish conversation
    article_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(article_start, pattern="^article$")],
        states={
            ARTICLE_FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, article_full_name)],
            ARTICLE_UNI: [MessageHandler(filters.TEXT & ~filters.COMMAND, article_uni)],
            ARTICLE_FACULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, article_faculty)],
            ARTICLE_DIRECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, article_direction)],
            ARTICLE_COURSE: [CallbackQueryHandler(article_course, pattern="^course_")],
            ARTICLE_SUPERVISOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, article_supervisor)],
            ARTICLE_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, article_title)],
            ARTICLE_LANG: [CallbackQueryHandler(article_lang, pattern="^lang_")],
            ARTICLE_CONTACT: [
                CallbackQueryHandler(article_contact_choice, pattern="^contact_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, article_contact_input),
            ],
            ARTICLE_EMAIL: [
                CallbackQueryHandler(article_email_choice, pattern="^email_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, article_email_input),
            ],
            ARTICLE_CONFIRM: [
                CallbackQueryHandler(article_confirm, pattern="^article_(confirm|cancel)$")
            ],
            ARTICLE_WAIT_CHECK: [
                CallbackQueryHandler(article_send_check, pattern="^send_check_article$"),
                MessageHandler(filters.PHOTO, article_receive_check),
            ],
            ARTICLE_WAIT_FINAL: [],
        },
        fallbacks=[CommandHandler("start", start)],
        per_user=True,
    )

    # Scopus maqola conversation
    scopus_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(scopus_start, pattern="^scopus$")],
        states={
            SCOPUS_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, scopus_name)],
            SCOPUS_UNI: [MessageHandler(filters.TEXT & ~filters.COMMAND, scopus_uni)],
            SCOPUS_FACULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, scopus_faculty)],
            SCOPUS_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, scopus_city)],
            SCOPUS_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, scopus_email)],
            SCOPUS_ORCID: [
                CallbackQueryHandler(scopus_orcid_choice, pattern="^orcid_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, scopus_orcid_input),
            ],
            SCOPUS_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, scopus_title)],
            SCOPUS_LANG: [CallbackQueryHandler(scopus_lang, pattern="^slang_")],
            SCOPUS_CONFIRM: [CallbackQueryHandler(scopus_confirm, pattern="^scopus_(confirm|cancel)$")],
            SCOPUS_WAIT_CHECK: [
                CallbackQueryHandler(scopus_send_check, pattern="^send_check_scopus$"),
                MessageHandler(filters.PHOTO, scopus_receive_check),
            ],
            SCOPUS_WAIT_FINAL: [],
        },
        fallbacks=[CommandHandler("start", start)],
        per_user=True,
    )

    # Handlers qo'shish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin_help", admin_help))
    app.add_handler(CommandHandler("ready", admin_article_ready))
    app.add_handler(CommandHandler("send_article", admin_send_article))
    app.add_handler(article_conv)
    app.add_handler(scopus_conv)

    # Admin callback handlers
    app.add_handler(CallbackQueryHandler(admin_check_approve, pattern="^approve_check_"))
    app.add_handler(CallbackQueryHandler(admin_check_reject, pattern="^reject_check_"))
    app.add_handler(CallbackQueryHandler(final_check_callback, pattern="^final_check_"))
    app.add_handler(CallbackQueryHandler(final_approve, pattern="^final_approve_"))
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^(about|back_main)$"))

    # Admin maqola yuborish (document/text)
    app.add_handler(MessageHandler(
        filters.User(ADMIN_ID) & (filters.Document.ALL | filters.TEXT) & ~filters.COMMAND,
        admin_forward_article
    ))

    # Yakuniy to'lov cheki
    app.add_handler(MessageHandler(filters.PHOTO & ~filters.User(ADMIN_ID), final_check_receive))

    print("🤖 Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
