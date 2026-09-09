from aiogram import Router, F
from aiogram.types import Message

from config import ALLOWED_USER_IDS, TOPICS
from database import get_modules


router = Router()


@router.message(F.text == "📚 آموزش جامع")
async def education_menu(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    modules = await get_modules()

    text = "📚 <b>آموزش جامع</b>\n\n"

    for index, module in enumerate(modules, 1):
        text += (
            f"{index}. {module['title']}\n"
        )

    text += (
        "\n📌 مسیر آموزش شامل آموزش مفهومی، مثال، "
        "نکات تخصصی، نکات آزمونی، فلش‌کارت و آزمون خواهد بود."
    )

    await message.answer(text)


@router.message(F.text.startswith("درس "))
async def lesson_handler(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    lesson = message.text[4:].strip()

    await message.answer(
        f"📖 <b>{lesson}</b>\n\n"
        "محتوای کامل این درس در مرحله توسعه محتوای آموزشی "
        "به بانک دروس اضافه می‌شود.\n\n"
        "ساختار درس:\n"
        "• آموزش مفهومی\n"
        "• مثال\n"
        "• نکات تخصصی\n"
        "• نکات آزمونی\n"
        "• خلاصه\n"
        "• فلش‌کارت\n"
        "• تست چهارگزینه‌ای"
    )
