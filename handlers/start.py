"""
AliDaneshYarBot
Main start handler and main menu.
"""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from config import ALLOWED_USER_IDS, BOT_NAME
from database import register_user


router = Router()


# ============================================================
# MAIN KEYBOARD
# ============================================================

def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📚 آموزش جامع"),
                KeyboardButton(text="🎯 آزمون‌های استخدامی"),
            ],
            [
                KeyboardButton(text="🔬 تحقیق و مقالات"),
                KeyboardButton(text="🔎 جستجوی هوشمند"),
            ],
            [
                KeyboardButton(text="📄 کتابخانه شخصی"),
                KeyboardButton(text="🧠 ابزار مطالعه"),
            ],
            [
                KeyboardButton(text="📅 برنامه مطالعه"),
                KeyboardButton(text="⭐ ذخیره‌شده‌ها"),
            ],
            [
                KeyboardButton(text="⚙️ تنظیمات"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="یک گزینه را انتخاب کنید...",
    )


# ============================================================
# ACCESS CHECK
# ============================================================

def is_allowed_user(user_id: int) -> bool:
    return user_id in ALLOWED_USER_IDS


# ============================================================
# REGISTER USER
# ============================================================

async def ensure_user_registered(message: Message) -> bool:
    if message.from_user is None:
        return False

    user_id = message.from_user.id

    if not is_allowed_user(user_id):
        return False

    await register_user(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    return True


# ============================================================
# WELCOME TEXT
# ============================================================

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
        "دستیار شخصی تو برای:\n"
        "📚 آموزش و یادگیری\n"
        "🔬 تحقیق و مقالات علمی\n"
        "🎯 آمادگی آزمون‌های استخدامی\n"
        "🏦 بانکداری و آزمون‌های بانکی\n"
        "📊 مدیریت، مالی و حسابداری\n"
        "📈 بازاریابی و فروش\n"
        "🌍 تجارت بین‌الملل\n"
        "🇬🇧 آموزش زبان انگلیسی\n"
        "🧠 آزمون، فلش‌کارت و مرور\n"
        "📅 برنامه‌ریزی مطالعه\n\n"
        "از منوی زیر بخش موردنظرت را انتخاب کن:"
    )


# ============================================================
# SEND MAIN MENU
# ============================================================

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


# ============================================================
# /START
# ============================================================

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


# ============================================================
# /MENU
# ============================================================

@router.message(lambda message: message.text == "/menu")
async def menu_handler(message: Message) -> None:

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
