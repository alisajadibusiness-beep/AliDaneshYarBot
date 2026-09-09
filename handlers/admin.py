from aiogram import Router, F
from aiogram.types import Message

from config import ALLOWED_USER_IDS


router = Router()


@router.message(F.text == "⚙️ تنظیمات")
async def settings(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    await message.answer(
        "⚙️ <b>تنظیمات ربات</b>\n\n"
        "🔐 دسترسی: خصوصی\n"
        "🔬 پایش منابع: فعال\n"
        "📰 دریافت منابع جدید: فعال\n"
        "📚 دسته‌بندی علمی: فعال\n"
        "🧹 حذف موارد تکراری: فعال\n"
        "📄 اولویت Open Access: فعال\n"
        "⏱ بررسی خودکار: هر ۲۴ ساعت"
    )


@router.message(F.text == "📡 وضعیت")
async def status(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    await message.answer(
        "🟢 <b>AliDaneshYarBot</b>\n\n"
        "وضعیت ربات: فعال\n"
        "دسترسی: خصوصی\n"
        "پایگاه داده: SQLite\n"
        "جستجوی علمی: فعال\n"
        "پایش خودکار منابع: فعال"
    )
