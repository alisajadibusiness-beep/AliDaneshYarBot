from aiogram import Router, F
from aiogram.types import Message

from config import ALLOWED_USER_IDS


router = Router()


@router.message(F.text == "📅 برنامه مطالعه")
async def study_plan(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    await message.answer(
        "📅 <b>برنامه مطالعه</b>\n\n"
        "امکانات:\n"
        "• برنامه روزانه\n"
        "• برنامه هفتگی\n"
        "• تعیین هدف\n"
        "• یادآوری مطالعه\n"
        "• گزارش عملکرد\n"
        "• پیگیری آمادگی آزمون\n\n"
        "ساختار برنامه بر اساس زمان آزاد، "
        "هدف و اولویت دروس تنظیم خواهد شد."
    )
