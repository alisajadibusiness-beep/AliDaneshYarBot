from aiogram import Router, F
from aiogram.types import Message

from config import ALLOWED_USER_IDS
from database import search_articles


router = Router()


@router.message(F.text == "🔬 تحقیق و مقالات")
async def articles_menu(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    results = await search_articles(
        query="",
        limit=10,
    )

    if not results:
        await message.answer(
            "هنوز مقاله‌ای در پایگاه داخلی ثبت نشده است.\n\n"
            "سیستم جستجوی خودکار منابع به‌صورت دوره‌ای "
            "منابع جدید را دریافت خواهد کرد."
        )
        return

    text = "🔬 <b>مقالات ذخیره‌شده</b>\n\n"

    for article in results:
        text += (
            f"• <b>{article['title']}</b>\n"
            f"منبع: {article['source']}\n"
        )

        if article["url"]:
            text += f"{article['url']}\n"

        text += "\n"

    await message.answer(
        text,
        disable_web_page_preview=True,
    )
