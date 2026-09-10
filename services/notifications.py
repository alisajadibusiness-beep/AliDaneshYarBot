from aiogram import Bot

from config import ALLOWED_USER_IDS


async def notify_owner(
    bot: Bot,
    text: str,
) -> None:
    for user_id in ALLOWED_USER_IDS:
        try:
            await bot.send_message(
                user_id,
                text,
            )
        except Exception:
            continue
