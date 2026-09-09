from aiogram import Router, F
from aiogram.types import Message

from config import ALLOWED_USER_IDS
from database import get_progress


router = Router()


@router.message(F.text == "📊 آمار پیشرفت")
async def progress(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    rows = await get_progress(
        message.from_user.id
    )

    if not rows:
        await message.answer(
            "📊 هنوز فعالیت آموزشی ثبت نشده است."
        )
        return

    completed = sum(
        1 for row in rows
        if row["completed"]
    )

    await message.answer(
        "📊 <b>آمار پیشرفت</b>\n\n"
        f"تعداد فعالیت‌ها: {len(rows)}\n"
        f"تکمیل‌شده: {completed}\n"
        f"درصد تکمیل: "
        f"{round(completed * 100 / len(rows), 1)}%"
    )
