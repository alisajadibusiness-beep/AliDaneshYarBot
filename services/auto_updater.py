"""
AliDaneshYarBot
Automatic scientific resource updater.
"""

import asyncio
import logging
from typing import Optional

from aiogram import Bot

from config import (
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


# ============================================================
# UPDATE RESULT
# ============================================================

_last_update_count: int = 0
_last_update_success: bool = False


def get_last_update_count() -> int:
    return _last_update_count


def get_last_update_status() -> bool:
    return _last_update_success


# ============================================================
# RUN UPDATE
# ============================================================

async def run_update(
    bot: Optional[Bot] = None,
    notify_user: bool = False,
) -> int:

    global _last_update_count
    global _last_update_success

    try:

        logger.info(
            "Starting automatic resource update..."
        )

        count = await collect_latest_resources(
            limit_per_topic=AUTO_UPDATE_LIMIT
        )

        _last_update_count = int(count or 0)
        _last_update_success = True

        logger.info(
            "Automatic resource update completed. "
            "Processed %s resources.",
            _last_update_count,
        )

        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        # The updater does NOT send a message automatically
        # unless explicitly requested.
        #
        # This prevents the research report from appearing
        # instead of the main menu when the bot starts.
        # ----------------------------------------------------

        if (
            notify_user
            and bot is not None
            and _last_update_count > 0
        ):
            try:

                from config import ALLOWED_USER_IDS

                for user_id in ALLOWED_USER_IDS:

                    try:

                        await bot.send_message(
                            user_id,
                            (
                                "🔬 <b>گزارش پایش منابع</b>\n\n"
                                "بررسی منابع جدید انجام شد.\n"
                                f"تعداد منابع پردازش‌شده: "
                                f"{_last_update_count}\n\n"
                                "برای مشاهده منابع جدید، "
                                "وارد بخش «🔬 تحقیق و مقالات» شوید."
                            ),
                            parse_mode="HTML",
                        )

                    except Exception:
                        logger.exception(
                            "Could not notify user %s.",
                            user_id,
                        )

            except Exception:
                logger.exception(
                    "Could not send update notification."
                )

        return _last_update_count

    except Exception:

        _last_update_success = False

        logger.exception(
            "Automatic resource update failed."
        )

        return 0


# ============================================================
# AUTOMATIC LOOP
# ============================================================

async def auto_update_loop(
    bot: Bot,
) -> None:

    if not AUTO_UPDATE_ENABLED:

        logger.info(
            "Automatic updater is disabled."
        )

        return

    logger.info(
        "Automatic updater enabled."
    )

    logger.info(
        "Update interval: %s hours.",
        AUTO_UPDATE_INTERVAL_HOURS,
    )

    # --------------------------------------------------------
    # Initial delay
    # --------------------------------------------------------
    #
    # Give Telegram polling and the main menu time to start.
    # --------------------------------------------------------

    await asyncio.sleep(30)

    while True:

        try:

            await run_update(
                bot=bot,
                notify_user=False,
            )

        except asyncio.CancelledError:

            logger.info(
                "Automatic updater cancelled."
            )

            raise

        except Exception:

            logger.exception(
                "Unexpected updater error."
            )

        # ----------------------------------------------------
        # Wait for next scan
        # ----------------------------------------------------

        await asyncio.sleep(
            AUTO_UPDATE_INTERVAL_HOURS
            * 60
            * 60
        )
