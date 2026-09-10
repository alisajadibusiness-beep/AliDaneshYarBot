"""
AliDaneshYarBot
Main start handler + main menu navigation.
This file handles:
- /start
- /menu
- Main menu buttons
- Educational menu
- Employment exam menu
- Research/articles menu
- Smart search menu
- Personal library menu
- Study tools menu
- Study plan menu
- Saved items menu
- Settings menu
- Back buttons
- Unknown main-menu button fallback
Private bot:
Only ALLOWED_USER_IDS can use the bot.
"""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from config import (
    ALLOWED_USER_IDS,
    BOT_NAME,
)
from database import register_user
router = Router(name="start")
# ==========================================================
# Main Menu
# ==========================================================
MAIN_MENU = "🏠 منوی اصلی"
EDUCATION = "📚 آموزش جامع"
EXAMS = "🎯 آزمون‌های استخدامی"
ARTICLES = "🔬 تحقیق و مقالات"
SMART_SEARCH = "🔎 جستجوی هوشمند"
LIBRARY = "📄 کتابخانه شخصی"
STUDY_TOOLS = "🧠 ابزار مطالعه"
STUDY_PLAN = "📅 برنامه مطالعه"
SAVED = "⭐ ذخیره‌شده‌ها"
SETTINGS = "⚙️ تنظیمات"
def main_keyboard() -> ReplyKeyboardMarkup:
    """
    Main bot keyboard.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=EDUCATION),
                KeyboardButton(text=EXAMS),
            ],
            [
                KeyboardButton(text=ARTICLES),
                KeyboardButton(text=SMART_SEARCH),
            ],
            [
                KeyboardButton(text=LIBRARY),
                KeyboardButton(text=STUDY_TOOLS),
            ],
            [
                KeyboardButton(text=STUDY_PLAN),
                KeyboardButton(text=SAVED),
            ],
            [
                KeyboardButton(text=SETTINGS),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="یک گزینه را انتخاب کنید...",
    )
# ==========================================================
# Common Keyboards
# ==========================================================
def back_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=MAIN_MENU),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
def education_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📘 مدیریت و بازرگانی"),
                KeyboardButton(text="🏦 بانکداری"),
            ],
            [
                KeyboardButton(text="💰 مدیریت مالی"),
                KeyboardButton(text="🧾 حسابداری"),
            ],
            [
                KeyboardButton(text="📣 بازاریابی و فروش"),
                KeyboardButton(text="🌍 تجارت بین‌الملل"),
            ],
            [
                KeyboardButton(text="📐 دروس پایه مدیریت"),
                KeyboardButton(text="🇬🇧 زبان انگلیسی"),
            ],
            [
                KeyboardButton(text=MAIN_MENU),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
def exam_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📚 دروس عمومی"),
                KeyboardButton(text="📊 تخصصی مدیریت"),
            ],
            [
                KeyboardButton(text="🏛 مدیریت دولتی"),
                KeyboardButton(text="💼 مدیریت بازرگانی"),
            ],
            [
                KeyboardButton(text="🧾 حسابداری"),
                KeyboardButton(text="📈 اقتصاد"),
            ],
            [
                KeyboardButton(text="🏦 بانکداری"),
                KeyboardButton(text="🇬🇧 زبان انگلیسی"),
            ],
            [
                KeyboardButton(text="💻 فناوری اطلاعات و ICDL"),
                KeyboardButton(text="🧠 هوش و استعداد"),
            ],
            [
                KeyboardButton(text="➗ ریاضی و آمار"),
            ],
            [
                KeyboardButton(text=MAIN_MENU),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
def research_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🆕 مقالات جدید"),
                KeyboardButton(text="🌐 مقالات خارجی"),
            ],
            [
                KeyboardButton(text="🔬 مقالات علمی"),
                KeyboardButton(text="🔎 جستجوی Crossref"),
            ],
            [
                KeyboardButton(text="🚀 جستجوی arXiv"),
                KeyboardButton(text="🔓 مقالات Open Access"),
            ],
            [
                KeyboardButton(text="🇮🇷 ترجمه فارسی"),
                KeyboardButton(text="⭐ ذخیره مقاله"),
            ],
            [
                KeyboardButton(text=MAIN_MENU),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
def search_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔍 جستجوی مقاله"),
            ],
            [
                KeyboardButton(text="🆕 جدیدترین منابع"),
                KeyboardButton(text="📚 جستجوی آموزشی"),
            ],
            [
                KeyboardButton(text="🏦 جستجوی بانکداری"),
                KeyboardButton(text="📊 جستجوی مدیریت"),
            ],
            [
                KeyboardButton(text="🌍 جستجوی تجارت بین‌الملل"),
                KeyboardButton(text="🤖 جستجوی هوش مصنوعی"),
            ],
            [
                KeyboardButton(text=MAIN_MENU),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
def library_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📁 فایل‌های من"),
                KeyboardButton(text="📕 PDFها"),
            ],
            [
                KeyboardButton(text="📝 جزوه‌ها"),
                KeyboardButton(text="🔬 مقالات ذخیره‌شده"),
            ],
            [
                KeyboardButton(text="🔎 جستجو در فایل‌ها"),
            ],
            [
                KeyboardButton(text=MAIN_MENU),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
def study_tools_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🧠 آزمون هوشمند"),
                KeyboardButton(text="🃏 فلش‌کارت"),
            ],
            [
                KeyboardButton(text="🔄 مرور مطالب"),
                KeyboardButton(text="❓ آزمونک"),
            ],
            [
                KeyboardButton(text="⚠️ نقاط ضعف"),
                KeyboardButton(text="📊 آمار پیشرفت"),
            ],
            [
                KeyboardButton(text=MAIN_MENU),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
def study_plan_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📅 برنامه روزانه"),
                KeyboardButton(text="🗓 برنامه هفتگی"),
            ],
            [
                KeyboardButton(text="⏰ یادآوری"),
                KeyboardButton(text="📊 گزارش مطالعه"),
            ],
            [
                KeyboardButton(text=MAIN_MENU),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
def settings_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="👤 پروفایل"),
                KeyboardButton(text="🔔 اعلان‌ها"),
            ],
            [
                KeyboardButton(text="🔬 موضوعات مورد علاقه"),
                KeyboardButton(text="🌐 منابع علمی"),
            ],
            [
                KeyboardButton(text="ℹ️ درباره ربات"),
            ],
            [
                KeyboardButton(text=MAIN_MENU),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
# ==========================================================
# Educational Module Keyboard
# ==========================================================
def educational_module_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📖 شروع یادگیری"),
            ],
            [
                KeyboardButton(text="📚 فصل‌ها"),
                KeyboardButton(text="🧠 آزمون این درس"),
            ],
            [
                KeyboardButton(text="🃏 فلش‌کارت"),
                KeyboardButton(text="⭐ ذخیره"),
            ],
            [
                KeyboardButton(text=EDUCATION),
            ],
            [
                KeyboardButton(text=MAIN_MENU),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
# ==========================================================
# Security
# ==========================================================
def is_allowed_user(user_id: int) -> bool:
    return user_id in ALLOWED_USER_IDS
async def ensure_user_registered(message: Message) -> bool:
    """
    Register the user if the user is allowed.
    """
    if message.from_user is None:
        return False
    user_id = message.from_user.id
    if not is_allowed_user(user_id):
        return False
    try:
        await register_user(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
    except Exception:
        # Registration failure must not prevent menu usage.
        pass
    return True
# ==========================================================
# Welcome
# ==========================================================
def welcome_text(message: Message) -> str:
    first_name = (
        message.from_user.first_name
        if message.from_user
        else None
    )
    name = first_name or "دوست من"
    return (
        f"سلام {name} 👋\n\n"
        f"🧠 <b>{BOT_NAME}</b>\n\n"
        "دستیار شخصی تو برای:\n\n"
        "📚 آموزش جامع\n"
        "🔬 تحقیق و مقالات علمی\n"
        "🎯 آمادگی آزمون‌های استخدامی\n"
        "🏦 بانکداری و آزمون‌های بانکی\n"
        "📊 مدیریت، مالی و حسابداری\n"
        "📣 بازاریابی و فروش\n"
        "🌍 تجارت بین‌الملل\n"
        "🇬🇧 زبان انگلیسی\n"
        "🧠 آزمون و فلش‌کارت\n"
        "📅 برنامه مطالعه\n\n"
        "از منوی زیر انتخاب کن:"
    )
# ==========================================================
# Main Menu Sender
# ==========================================================
async def send_main_menu(
    message: Message,
    show_welcome: bool = True,
) -> None:
    if message.from_user is None:
        return
    if not is_allowed_user(message.from_user.id):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await ensure_user_registered(message)
    if show_welcome:
        text = welcome_text(message)
    else:
        text = (
            "🏠 <b>منوی اصلی علی دانش‌یار</b>\n\n"
            "یک بخش را انتخاب کن:"
        )
    await message.answer(
        text,
        reply_markup=main_keyboard(),
        parse_mode="HTML",
    )
# ==========================================================
# /start
# ==========================================================
@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    if message.from_user is None:
        return
    if not is_allowed_user(message.from_user.id):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await send_main_menu(
        message,
        show_welcome=True,
    )
# ==========================================================
# /menu
# ==========================================================
@router.message(lambda message: message.text == "/menu")
async def menu_command_handler(message: Message) -> None:
    if message.from_user is None:
        return
    if not is_allowed_user(message.from_user.id):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await send_main_menu(
        message,
        show_welcome=False,
    )
# ==========================================================
# Main Menu Button Handlers
# ==========================================================
@router.message(lambda message: message.text == MAIN_MENU)
async def main_menu_button_handler(message: Message) -> None:
    await send_main_menu(
        message,
        show_welcome=False,
    )
@router.message(lambda message: message.text == EDUCATION)
async def education_menu_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await message.answer(
        "📚 <b>آموزش جامع</b>\n\n"
        "رشته و حوزه موردنظر را انتخاب کن:\n\n"
        "مدیریت، بانکداری، مالی، حسابداری، "
        "بازاریابی، تجارت بین‌الملل، دروس پایه "
        "و زبان انگلیسی.",
        reply_markup=education_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == EXAMS)
async def exams_menu_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await message.answer(
        "🎯 <b>آزمون‌های استخدامی</b>\n\n"
        "بخش موردنظر را انتخاب کن.\n\n"
        "منابع عمومی و تخصصی به صورت جداگانه "
        "در دسترس خواهند بود.",
        reply_markup=exam_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == ARTICLES)
async def articles_menu_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await message.answer(
        "🔬 <b>تحقیق و مقالات</b>\n\n"
        "از این بخش می‌توانی منابع علمی جدید، "
        "مقالات خارجی، منابع Open Access و "
        "جستجوی علمی را دنبال کنی.",
        reply_markup=research_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == SMART_SEARCH)
async def smart_search_menu_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await message.answer(
        "🔎 <b>جستجوی هوشمند</b>\n\n"
        "موضوع موردنظر را انتخاب کن یا جستجوی "
        "آزاد انجام بده.\n\n"
        "در نسخه کامل، جستجو بین منابع علمی، "
        "آموزشی و کتابخانه شخصی انجام می‌شود.",
        reply_markup=search_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == LIBRARY)
async def library_menu_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await message.answer(
        "📄 <b>کتابخانه شخصی</b>\n\n"
        "فایل‌ها، PDFها، جزوه‌ها و مقالات "
        "ذخیره‌شده خودت را از این بخش مدیریت کن.",
        reply_markup=library_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == STUDY_TOOLS)
async def study_tools_menu_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await message.answer(
        "🧠 <b>ابزار مطالعه</b>\n\n"
        "آزمون هوشمند، فلش‌کارت، مرور، "
        "آزمونک و آمار پیشرفت.",
        reply_markup=study_tools_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == STUDY_PLAN)
async def study_plan_menu_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await message.answer(
        "📅 <b>برنامه مطالعه</b>\n\n"
        "برنامه روزانه و هفتگی، یادآوری و "
        "گزارش مطالعه از این بخش مدیریت می‌شود.",
        reply_markup=study_plan_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == SAVED)
async def saved_menu_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await message.answer(
        "⭐ <b>ذخیره‌شده‌ها</b>\n\n"
        "اینجا محل دسترسی سریع به مقالات، "
        "درس‌ها، فلش‌کارت‌ها و منابع ذخیره‌شده است.",
        reply_markup=back_main_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == SETTINGS)
async def settings_menu_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await message.answer(
        "⚙️ <b>تنظیمات</b>\n\n"
        "تنظیمات شخصی، اعلان‌ها، موضوعات "
        "موردعلاقه و منابع علمی.",
        reply_markup=settings_keyboard(),
        parse_mode="HTML",
    )
# ==========================================================
# Educational Buttons
# ==========================================================
EDUCATIONAL_BUTTONS = {
    "📘 مدیریت و بازرگانی": (
        "📘 مدیریت و بازرگانی",
        "مدیریت عمومی، رفتار سازمانی، منابع انسانی، "
        "مدیریت استراتژیک، رهبری، تصمیم‌گیری، "
        "عملیات، پروژه و کسب‌وکار."
    ),
    "🏦 بانکداری": (
        "🏦 بانکداری",
        "بانک‌ها، بانک مرکزی، عملیات بانکی، سپرده‌ها، "
        "تسهیلات، اعتبارسنجی، ریسک، بانکداری دیجیتال، "
        "AML و مباحث آزمون استخدامی بانک‌ها."
    ),
    "💰 مدیریت مالی": (
        "💰 مدیریت مالی",
        "ارزش زمانی پول، ریسک و بازده، بودجه‌بندی سرمایه‌ای، "
        "NPV، IRR، ساختار سرمایه، اهرم، سرمایه در گردش "
        "و تحلیل مالی."
    ),
    "🧾 حسابداری": (
        "🧾 حسابداری",
        "اصول حسابداری، ثبت معاملات، دفتر روزنامه، "
        "دفتر کل، صورت‌های مالی، موجودی، دارایی ثابت، "
        "بهای تمام‌شده، حسابداری مدیریت و حسابرسی."
    ),
    "📣 بازاریابی و فروش": (
        "📣 بازاریابی و فروش",
        "بازاریابی، رفتار مصرف‌کننده، STP، محصول، قیمت، "
        "توزیع، تبلیغات، برند، دیجیتال مارکتینگ، فروش، "
        "مذاکره و CRM."
    ),
    "🌍 تجارت بین‌الملل": (
        "🌍 تجارت بین‌الملل",
        "نظریه‌های تجارت، سیاست تجاری، صادرات و واردات، "
        "قراردادها، Incoterms، اسناد تجاری، حمل‌ونقل، "
        "اعتبار اسنادی، گمرک، ریسک و تجارت دیجیتال."
    ),
    "📐 دروس پایه مدیریت": (
        "📐 دروس پایه مدیریت",
        "اقتصاد خرد و کلان، ریاضی، آمار، تحقیق در عملیات، "
        "روش تحقیق، حقوق بازرگانی، سیستم‌های اطلاعاتی "
        "و اقتصاد مدیریتی."
    ),
    "🇬🇧 زبان انگلیسی": (
        "🇬🇧 زبان انگلیسی",
        "آموزش انگلیسی از سطح صفر تا پیشرفته، "
        "گرامر، واژگان، مکالمه، Reading، Writing، "
        "Academic English و Business English."
    ),
}
@router.message(
    lambda message: message.text in EDUCATIONAL_BUTTONS
)
async def educational_module_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    title, description = EDUCATIONAL_BUTTONS[
        message.text
    ]
    await message.answer(
        f"<b>{title}</b>\n\n"
        f"{description}\n\n"
        "📚 ساختار یادگیری:\n"
        "درس → آموزش مفهومی → نکات تخصصی → "
        "مثال → نکات آزمونی → خلاصه → فلش‌کارت → آزمون\n\n"
        "برای شروع یادگیری از گزینه زیر استفاده کن.",
        reply_markup=educational_module_keyboard(),
        parse_mode="HTML",
    )
# ==========================================================
# Education Actions
# ==========================================================
@router.message(lambda message: message.text == "📖 شروع یادگیری")
async def start_learning_handler(message: Message) -> None:
    await message.answer(
        "📖 <b>شروع یادگیری</b>\n\n"
        "سیستم آموزشی آماده است.\n\n"
        "هر درس در نسخه کامل شامل:\n"
        "• آموزش مفهومی\n"
        "• اصطلاحات کلیدی\n"
        "• نکات تخصصی\n"
        "• مثال واقعی\n"
        "• مطالعه موردی\n"
        "• نکات آزمونی\n"
        "• خلاصه\n"
        "• فلش‌کارت\n"
        "• تست چهارگزینه‌ای\n"
        "• پاسخ تشریحی\n\n"
        "محتوای هر ماژول از فایل داده همان رشته "
        "خوانده خواهد شد."
        ,
        reply_markup=educational_module_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == "📚 فصل‌ها")
async def chapters_handler(message: Message) -> None:
    await message.answer(
        "📚 <b>فصل‌ها</b>\n\n"
        "فصل‌های آموزشی بر اساس ماژول انتخاب‌شده "
        "نمایش داده می‌شوند.\n\n"
        "ساختار پیشنهادی:\n"
        "فصل ۱ → مفاهیم پایه\n"
        "فصل ۲ → مفاهیم تخصصی\n"
        "فصل ۳ → کاربردها\n"
        "فصل ۴ → تحلیل و تصمیم‌گیری\n"
        "فصل ۵ → آزمون و مرور",
        reply_markup=educational_module_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == "🧠 آزمون این درس")
async def lesson_quiz_handler(message: Message) -> None:
    await message.answer(
        "🧠 <b>آزمون این درس</b>\n\n"
        "سیستم آزمون آماده است.\n\n"
        "در نسخه کامل، سوال‌ها از بانک سوال "
        "همان درس انتخاب می‌شوند و نتیجه، درصد "
        "و نقاط ضعف ثبت خواهد شد.",
        reply_markup=educational_module_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == "🃏 فلش‌کارت")
async def education_flashcard_handler(message: Message) -> None:
    await message.answer(
        "🃏 <b>فلش‌کارت</b>\n\n"
        "فلش‌کارت‌های درس انتخاب‌شده برای "
        "مرور سریع نمایش داده می‌شوند.",
        reply_markup=educational_module_keyboard(),
        parse_mode="HTML",
    )
@router.message(lambda message: message.text == "⭐ ذخیره")
async def education_save_handler(message: Message) -> None:
    await message.answer(
        "⭐ این بخش برای ذخیره درس و دسترسی "
        "سریع از قسمت «ذخیره‌شده‌ها» طراحی شده است."
    )
# ==========================================================
# Employment Exam Buttons
# ==========================================================
EXAM_BUTTONS = {
    "📚 دروس عمومی": "دروس عمومی آزمون‌های استخدامی",
    "📊 تخصصی مدیریت": "دروس تخصصی مدیریت",
    "🏛 مدیریت دولتی": "مدیریت دولتی",
    "💼 مدیریت بازرگانی": "مدیریت بازرگانی",
    "🧾 حسابداری": "حسابداری",
    "📈 اقتصاد": "اقتصاد",
    "🏦 بانکداری": "بانکداری",
    "🇬🇧 زبان انگلیسی": "زبان انگلیسی",
    "💻 فناوری اطلاعات و ICDL": "فناوری اطلاعات و ICDL",
    "🧠 هوش و استعداد": "هوش و استعداد",
    "➗ ریاضی و آمار": "ریاضی و آمار",
}
@router.message(lambda message: message.text in EXAM_BUTTONS)
async def exam_subject_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    title = EXAM_BUTTONS[
        message.text
    ]
    await message.answer(
        f"🎯 <b>{title}</b>\n\n"
        "این بخش برای مطالعه و تمرین آزمون‌های "
        "استخدامی طراحی شده است.\n\n"
        "امکانات:\n"
        "📖 درسنامه\n"
        "🧠 تست چهارگزینه‌ای\n"
        "💡 نکات آزمونی\n"
        "📊 ثبت درصد\n"
        "⚠️ تحلیل نقاط ضعف\n"
        "🔄 مرور اشتباهات\n\n"
        "نکته: منابع تخصصی بسته به سازمان، سال "
        "آزمون و عنوان شغلی می‌توانند متفاوت باشند.",
        reply_markup=exam_keyboard(),
        parse_mode="HTML",
    )
# ==========================================================
# Research Buttons
# ==========================================================
RESEARCH_BUTTONS = {
    "🆕 مقالات جدید": (
        "🆕 مقالات جدید",
        "نمایش جدیدترین منابع علمی جمع‌آوری‌شده."
    ),
    "🌐 مقالات خارجی": (
        "🌐 مقالات خارجی",
        "جستجو و نمایش منابع علمی خارجی."
    ),
    "🔬 مقالات علمی": (
        "🔬 مقالات علمی",
        "جستجوی منابع علمی و پژوهشی."
    ),
    "🔎 جستجوی Crossref": (
        "🔎 جستجوی Crossref",
        "جستجو در Crossref."
    ),
    "🚀 جستجوی arXiv": (
        "🚀 جستجوی arXiv",
        "جستجو در arXiv برای حوزه‌های مرتبط."
    ),
    "🔓 مقالات Open Access": (
        "🔓 مقالات Open Access",
        "نمایش منابعی که دسترسی قانونی و آزاد دارند."
    ),
    "🇮🇷 ترجمه فارسی": (
        "🇮🇷 ترجمه فارسی",
        "ترجمه عنوان و چکیده و خلاصه حرفه‌ای فارسی."
    ),
    "⭐ ذخیره مقاله": (
        "⭐ ذخیره مقاله",
        "ذخیره مقاله برای مطالعه بعدی."
    ),
}
@router.message(lambda message: message.text in RESEARCH_BUTTONS)
async def research_action_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    title, description = RESEARCH_BUTTONS[
        message.text
    ]
    await message.answer(
        f"<b>{title}</b>\n\n"
        f"{description}\n\n"
        "🔧 اتصال این گزینه به سرویس علمی مربوطه "
        "در مرحله سرویس پژوهش انجام می‌شود.\n\n"
        "منابع پولی یا دارای حق نشر به صورت غیرقانونی "
        "بازنشر نمی‌شوند؛ لینک منبع یا نسخه Open Access "
        "استفاده خواهد شد.",
        reply_markup=research_keyboard(),
        parse_mode="HTML",
    )
# ==========================================================
# Smart Search Buttons
# ==========================================================
SEARCH_BUTTONS = {
    "🔍 جستجوی مقاله": "جستجوی مقاله",
    "🆕 جدیدترین منابع": "جدیدترین منابع",
    "📚 جستجوی آموزشی": "جستجوی آموزشی",
    "🏦 جستجوی بانکداری": "جستجوی بانکداری",
    "📊 جستجوی مدیریت": "جستجوی مدیریت",
    "🌍 جستجوی تجارت بین‌الملل": "جستجوی تجارت بین‌الملل",
    "🤖 جستجوی هوش مصنوعی": "جستجوی هوش مصنوعی",
}
@router.message(lambda message: message.text in SEARCH_BUTTONS)
async def search_action_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    title = SEARCH_BUTTONS[
        message.text
    ]
    await message.answer(
        f"🔎 <b>{title}</b>\n\n"
        "عبارت جستجو را ارسال کن.\n\n"
        "مثال:\n"
        "• مدیریت استراتژیک\n"
        "• banking risk\n"
        "• artificial intelligence in business\n"
        "• international trade\n\n"
        "در مرحله بعدی این پیام به موتور جستجوی "
        "علمی و آموزشی متصل می‌شود.",
        reply_markup=search_keyboard(),
        parse_mode="HTML",
    )
# ==========================================================
# Library Buttons
# ==========================================================
LIBRARY_BUTTONS = {
    "📁 فایل‌های من": "فایل‌های من",
    "📕 PDFها": "PDFها",
    "📝 جزوه‌ها": "جزوه‌ها",
    "🔬 مقالات ذخیره‌شده": "مقالات ذخیره‌شده",
    "🔎 جستجو در فایل‌ها": "جستجو در فایل‌ها",
}
@router.message(lambda message: message.text in LIBRARY_BUTTONS)
async def library_action_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    title = LIBRARY_BUTTONS[
        message.text
    ]
    await message.answer(
        f"📄 <b>{title}</b>\n\n"
        "کتابخانه شخصی برای نگهداری و بازیابی "
        "فایل‌ها، PDFها، جزوه‌ها و مقالات طراحی شده است.\n\n"
        "فایل‌های ارسالی کاربر در این بخش مدیریت خواهند شد.",
        reply_markup=library_keyboard(),
        parse_mode="HTML",
    )
# ==========================================================
# Study Tools
# ==========================================================
STUDY_TOOL_BUTTONS = {
    "🧠 آزمون هوشمند": "آزمون هوشمند",
    "🃏 فلش‌کارت": "فلش‌کارت",
    "🔄 مرور مطالب": "مرور مطالب",
    "❓ آزمونک": "آزمونک",
    "⚠️ نقاط ضعف": "نقاط ضعف",
    "📊 آمار پیشرفت": "آمار پیشرفت",
}
@router.message(
    lambda message: message.text in STUDY_TOOL_BUTTONS
)
async def study_tool_action_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    title = STUDY_TOOL_BUTTONS[
        message.text
    ]
    await message.answer(
        f"🧠 <b>{title}</b>\n\n"
        "این بخش از سیستم مطالعه شخصی علی دانش‌یار است.\n\n"
        "هدف:\n"
        "• سنجش یادگیری\n"
        "• ثبت عملکرد\n"
        "• شناسایی نقاط ضعف\n"
        "• مرور هوشمند\n"
        "• افزایش ماندگاری مطالب",
        reply_markup=study_tools_keyboard(),
        parse_mode="HTML",
    )
# ==========================================================
# Study Plan
# ==========================================================
STUDY_PLAN_BUTTONS = {
    "📅 برنامه روزانه": "برنامه روزانه",
    "🗓 برنامه هفتگی": "برنامه هفتگی",
    "⏰ یادآوری": "یادآوری",
    "📊 گزارش مطالعه": "گزارش مطالعه",
}
@router.message(
    lambda message: message.text in STUDY_PLAN_BUTTONS
)
async def study_plan_action_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    title = STUDY_PLAN_BUTTONS[
        message.text
    ]
    await message.answer(
        f"📅 <b>{title}</b>\n\n"
        "سیستم برنامه‌ریزی مطالعه برای مدیریت "
        "مطالعه روزانه و هفتگی طراحی شده است.\n\n"
        "اطلاعات مطالعه، زمان صرف‌شده، درس‌های "
        "خوانده‌شده و نتایج آزمون‌ها قابل ثبت خواهد بود.",
        reply_markup=study_plan_keyboard(),
        parse_mode="HTML",
    )
# ==========================================================
# Settings
# ==========================================================
SETTINGS_BUTTONS = {
    "👤 پروفایل": "پروفایل",
    "🔔 اعلان‌ها": "اعلان‌ها",
    "🔬 موضوعات مورد علاقه": "موضوعات مورد علاقه",
    "🌐 منابع علمی": "منابع علمی",
    "ℹ️ درباره ربات": "درباره ربات",
}
@router.message(
    lambda message: message.text in SETTINGS_BUTTONS
)
async def settings_action_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    title = SETTINGS_BUTTONS[
        message.text
    ]
    if title == "درباره ربات":
        text = (
            "ℹ️ <b>علی دانش‌یار</b>\n\n"
            "دستیار شخصی پژوهش، آموزش و آمادگی آزمون.\n\n"
            "قابلیت‌های اصلی:\n"
            "📚 آموزش\n"
            "🔬 پژوهش\n"
            "🎯 آزمون استخدامی\n"
            "🧠 ابزار مطالعه\n"
            "📄 کتابخانه شخصی\n"
            "📅 برنامه مطالعه\n"
            "🔎 جستجوی هوشمند\n\n"
            "این ربات خصوصی است و فقط کاربر مجاز "
            "می‌تواند از آن استفاده کند."
        )
    else:
        text = (
            f"⚙️ <b>{title}</b>\n\n"
            "این بخش آماده اتصال به تنظیمات "
            "شخصی ربات است."
        )
    await message.answer(
        text,
        reply_markup=settings_keyboard(),
        parse_mode="HTML",
    )
# ==========================================================
# Simple Commands
# ==========================================================
@router.message(lambda message: message.text == "/help")
async def help_handler(message: Message) -> None:
    if not await ensure_user_registered(message):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await message.answer(
        "ℹ️ <b>راهنمای علی دانش‌یار</b>\n\n"
        "/start → شروع ربات\n"
        "/menu → منوی اصلی\n"
        "/help → راهنما\n\n"
        "برای استفاده، یکی از دکمه‌های منو را انتخاب کن.",
        reply_markup=main_keyboard(),
        parse_mode="HTML",
    )
# ==========================================================
# Fallback
# ==========================================================
@router.message()
async def start_fallback_handler(message: Message) -> None:
    """
    Prevent silent failures for ordinary text messages
    that are not handled by another router.
    """
    if message.from_user is None:
        return
    if not is_allowed_user(message.from_user.id):
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return
    await ensure_user_registered(message)
    await message.answer(
        "پیامت دریافت شد، اما این گزینه هنوز "
        "به بخش مربوطه متصل نشده است.\n\n"
        "برای ادامه از منوی اصلی استفاده کن.",
        reply_markup=main_keyboard(),
    )
