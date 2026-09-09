from aiogram import Router, F
from aiogram.types import Message

from config import ALLOWED_USER_IDS
from database import get_bookmarks


router = Router()


@router.message(F.text == "📄 کتابخانه شخصی")
async def library_menu(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    await message.answer(
        "📄 <b>کتابخانه شخصی</b>\n\n"
        "این بخش برای نگهداری:\n"
        "• PDF\n"
        "• جزوه‌ها\n"
        "• مقالات\n"
        "• فایل‌های آموزشی\n"
        "• منابع آزمون\n"
        "• یادداشت‌های شخصی\n\n"
        "طراحی شده است."
    )


@router.message(F.text == "⭐ ذخیره‌شده‌ها")
async def bookmarks(message: Message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return

    rows = await get_bookmarks(
        message.from_user.id
    )

    if not rows:
        await message.answer(
            "⭐ هنوز چیزی ذخیره نکرده‌ای."
        )
        return

    text = "⭐ <b>ذخیره‌شده‌ها</b>\n\n"

    for row in rows:
        title = row["title"] or row["item_key"]

        text += f"• {title}\n"

        if row["url"]:
            text += f"{row['url']}\n"

        text += "\n"

    await message.answer(
        text,
        disable_web_page_preview=True,
    )
