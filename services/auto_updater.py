import asyncio
import logging

from aiogram import Bot

from config import (
    ALLOWED_USER_IDS,
    AUTO_UPDATE_ENABLED,
    AUTO_UPDATE_INTERVAL_HOURS,
    AUTO_UPDATE_LIMIT,
)

from services.article_collector import (
    collect_latest_resources,
)


logger = logging.getLogger(
    "AliDaneshYarBot.auto_updater"
)


async def run_update(bot: Bot) -> None:
    try:
        count = await collect_latest_resources(
            limit_per_topic=AUTO_UPDATE_LIMIT
        )

        logger.info(
            "Automatic resource update completed. "
            "Processed %s resources.",
            count,
        )

        if count and ALLOWED_USER_IDS:
            user_id = next(
                iter(ALLOWED_USER_IDS)
            )

            await bot.send_message(
                user_id,
                "🔬 <b>گزارش پایش منابع</b>\n\n"
                f"بررسی منابع جدید انجام شد.\n"
                f"تعداد منابع پردازش‌شده: {count}",
            )

    except Exception:
        logger.exception(
            "Automatic resource update failed."
        )


async def auto_update_loop(
    bot: Bot,
) -> None:
    if not AUTO_UPDATE_ENABLED:
        logger.info(
            "Automatic updater is disabled."
        )
        return

    await asyncio.sleep(10)

    while True:
        await run_update(bot)

        await asyncio.sleep(
            AUTO_UPDATE_INTERVAL_HOURS
            * 60
            * 60
        )
