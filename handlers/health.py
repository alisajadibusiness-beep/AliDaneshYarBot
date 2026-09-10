from aiogram import Router
from aiogram.types import Message

from config import ALLOWED_USER_IDS


router = Router()


@router.message(commands={"health"})
async def health(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    await message.answer(
        "🟢 AliDaneshYarBot فعال است."
    )
