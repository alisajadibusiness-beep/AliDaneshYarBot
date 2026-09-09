from aiogram import Router, F
from aiogram.types import Message

from config import ALLOWED_USER_IDS
from database import search_articles
from services.scientific_search import search_all_sources


router = Router()


@router.message(F.text == "🔎 جستجوی هوشمند")
async def smart_search(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    await message.answer(
        "🔎 عبارت جستجو را ارسال کن.\n\n"
        "مثال:\n"
        "مدیریت استراتژیک\n"
        "Artificial Intelligence in Banking\n"
        "international business"
    )


@router.message(
    F.text.regexp(
        r"^(مدیریت|بانکداری|حسابداری|بازاریابی|تجارت|هوش مصنوعی|finance|banking|marketing).+",
        mode="i",
    )
)
async def topic_search(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    query = message.text.strip()

    await message.answer(
        f"🔎 در حال جستجو برای:\n<b>{query}</b>\n\n"
        "لطفاً چند لحظه صبر کن..."
    )

    results = await search_all_sources(
        query=query,
        limit=8,
    )

    if not results:
        local = await search_articles(
            query=query,
            limit=8,
        )

        if local:
            results = [dict(row) for row in local]

    if not results:
        await message.answer(
            "نتیجه‌ای پیدا نشد."
        )
        return

    text = "🔬 <b>نتایج جستجو</b>\n\n"

    for index, article in enumerate(results, 1):
        title = article.get("title", "بدون عنوان")
        source = article.get("source", "")
        url = article.get("url", "")

        text += (
            f"<b>{index}. {title}</b>\n"
            f"منبع: {source}\n"
        )

        if url:
            text += f"🔗 {url}\n"

        text += "\n"

    await message.answer(
        text,
        disable_web_page_preview=True,
    )
