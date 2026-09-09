from aiogram import Router, F
from aiogram.types import Message

from config import ALLOWED_USER_IDS
from database import save_quiz_result


router = Router()


@router.message(F.text == "🧠 ابزار مطالعه")
async def study_tools(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    await message.answer(
        "🧠 <b>ابزار مطالعه</b>\n\n"
        "📝 آزمون هوشمند\n"
        "🃏 فلش‌کارت\n"
        "🔁 مرور مطالب\n"
        "🎯 آزمونک\n"
        "📊 نقاط ضعف\n"
        "📈 آمار پیشرفت"
    )


@router.message(F.text.startswith("آزمون "))
async def quiz_start(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    module = message.text[5:].strip()

    await message.answer(
        f"📝 آزمون <b>{module}</b>\n\n"
        "سیستم آزمون هوشمند آماده دریافت بانک "
        "سؤالات تخصصی این درس است."
    )
