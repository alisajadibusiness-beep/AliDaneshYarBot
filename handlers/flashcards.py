from aiogram import Router, F
from aiogram.types import Message

from config import ALLOWED_USER_IDS


router = Router()


@router.message(F.text == "🃏 فلش‌کارت")
async def flashcards(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    await message.answer(
        "🃏 <b>فلش‌کارت</b>\n\n"
        "فلش‌کارت‌ها برای مفاهیم مهم مدیریت، "
        "بانکداری، مالی، حسابداری، بازاریابی، "
        "تجارت بین‌الملل و زبان انگلیسی ایجاد خواهند شد."
    )
