from aiogram import Router, F
from aiogram.types import Message

from config import ALLOWED_USER_IDS


router = Router()


@router.message(F.text == "🎯 آزمون‌های استخدامی")
async def exams_menu(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    await message.answer(
        "🎯 <b>آزمون‌های استخدامی</b>\n\n"
        "بخش‌ها:\n\n"
        "🏛 آزمون‌های دستگاه‌های دولتی\n"
        "🏦 آزمون‌های استخدامی بانک‌ها\n"
        "📚 دروس عمومی\n"
        "📊 مدیریت بازرگانی\n"
        "🏢 مدیریت دولتی\n"
        "💰 اقتصاد\n"
        "🧾 حسابداری\n"
        "🧠 هوش و استعداد\n"
        "➗ ریاضی و آمار\n"
        "🇬🇧 زبان انگلیسی\n\n"
        "منابع هر آزمون بر اساس سال و عنوان شغلی "
        "جداگانه مدیریت خواهد شد."
    )
