from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from config import ALLOWED_USER_IDS, BOT_NAME
from database import register_user


router = Router()


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
    )


@router.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id

    if user_id not in ALLOWED_USER_IDS:
        await message.answer(
            "⛔ دسترسی به این ربات خصوصی است."
        )
        return

    await register_user(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    await message.answer(
        f"سلام {message.from_user.first_name or 'دوست من'} 👋\n\n"
        f"<b>{BOT_NAME}</b>\n"
        "دستیار شخصی پژوهش، آموزش و آمادگی آزمون توست.\n\n"
        "از منوی زیر شروع کن:",
        reply_markup=main_keyboard(),
    )
