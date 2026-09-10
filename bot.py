"""
AliDaneshYarBot
دستیار شخصی پژوهش، آموزش، تحقیق و آمادگی آزمون

ویژگی‌های اصلی:
- دسترسی خصوصی با ALLOWED_USER_IDS
- Telegram Bot با aiogram
- SQLite
- HTTP Health Server برای Render
- Automatic Research Updater
- ماژول‌های آموزش
- جستجوی علمی
- آزمون و فلش‌کارت
- کتابخانه شخصی
- برنامه مطالعه
"""

import asyncio
import logging
import sys
from contextlib import suppress


# ============================================================
# STARTUP DIAGNOSTIC
# ============================================================

print(">>> ALIDANESHYAR BOT.PY STARTED <<<", flush=True)


# ============================================================
# AIROGRAM
# ============================================================

from aiogram import Bot, Dispatcher


# ============================================================
# CONFIG
# ============================================================

from config import (
    BOT_TOKEN,
    ALLOWED_USER_IDS,
    EDUCATIONAL_MODULES,
    PORT,
    HOST,
    validate_config,
    get_config_summary,
)


# ============================================================
# DATABASE
# ============================================================

from database import (
    init_database,
    seed_modules,
)


# ============================================================
# HANDLERS
# ============================================================

from handlers.start import router as start_router
from handlers.search import router as search_router
from handlers.education import router as education_router
from handlers.exams import router as exams_router
from handlers.articles import router as articles_router
from handlers.library import router as library_router
from handlers.quiz import router as quiz_router
from handlers.flashcards import router as flashcards_router
from handlers.progress import router as progress_router
from handlers.study_plan import router as study_plan_router
from handlers.admin import router as admin_router


# ============================================================
# SERVICES
# ============================================================

from services.auto_updater import (
    auto_update_loop,
)


# ============================================================
# WEB / HEALTH
# ============================================================

from web.health_server import (
    start_health_server,
    stop_health_server,
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
    force=True,
)

logger = logging.getLogger("AliDaneshYarBot")


# ============================================================
# MAIN
# ============================================================

async def main() -> None:

    print(">>> MAIN FUNCTION STARTED <<<", flush=True)

    # --------------------------------------------------------
    # Configuration validation
    # --------------------------------------------------------

    logger.info("Validating configuration...")

    validate_config()

    config_summary = get_config_summary()

    logger.info(
        "Application: %s",
        config_summary.get("app_name"),
    )

    logger.info(
        "Bot name: %s",
        config_summary.get("bot_name"),
    )

    logger.info(
        "Allowed users: %s",
        config_summary.get("allowed_users"),
    )

    logger.info(
        "Private access: %s",
        config_summary.get("private_access"),
    )

    logger.info(
        "Host: %s",
        HOST,
    )

    logger.info(
        "Port: %s",
        PORT,
    )


    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    logger.info("Initializing database...")

    await init_database()

    logger.info("Database initialized successfully.")


    # --------------------------------------------------------
    # Educational modules
    # --------------------------------------------------------

    logger.info(
        "Initializing %s educational modules...",
        len(EDUCATIONAL_MODULES),
    )

    await seed_modules(
        EDUCATIONAL_MODULES
    )

    logger.info(
        "Educational modules initialized successfully."
    )


    # --------------------------------------------------------
    # Telegram Bot
    # --------------------------------------------------------

    logger.info("Creating Telegram Bot instance...")

    bot = Bot(
        token=BOT_TOKEN,
    )

    dp = Dispatcher()

    logger.info("Telegram Dispatcher created.")


    # --------------------------------------------------------
    # Register routers
    # --------------------------------------------------------

    logger.info("Registering handlers...")

    dp.include_router(start_router)
    dp.include_router(search_router)
    dp.include_router(education_router)
    dp.include_router(exams_router)
    dp.include_router(articles_router)
    dp.include_router(library_router)
    dp.include_router(quiz_router)
    dp.include_router(flashcards_router)
    dp.include_router(progress_router)
    dp.include_router(study_plan_router)
    dp.include_router(admin_router)

    logger.info(
        "All Telegram handlers registered successfully."
    )


    # --------------------------------------------------------
    # Health server
    # --------------------------------------------------------

    health_runner = None

    # --------------------------------------------------------
    # Auto updater task
    # --------------------------------------------------------

    updater_task = None

    try:

        logger.info(
            "Starting HTTP health server on %s:%s...",
            HOST,
            PORT,
        )

        health_runner = await start_health_server(
            host=HOST,
            port=PORT,
        )

        logger.info(
            "HTTP health server started successfully."
        )

        logger.info(
            "Health endpoint: http://0.0.0.0:%s/health",
            PORT,
        )


        # ----------------------------------------------------
        # Telegram webhook
        # ----------------------------------------------------

        logger.info(
            "Removing existing Telegram webhook..."
        )

        try:

            await bot.delete_webhook(
                drop_pending_updates=True,
            )

            logger.info(
                "Telegram webhook removed successfully."
            )

        except Exception:

            logger.exception(
                "Could not remove Telegram webhook."
            )


        # ----------------------------------------------------
        # Automatic research updater
        # ----------------------------------------------------

        logger.info(
            "Starting automatic research updater..."
        )

        updater_task = asyncio.create_task(
            auto_update_loop(bot)
        )

        logger.info(
            "Automatic research updater started."
        )


        # ----------------------------------------------------
        # Telegram polling
        # ----------------------------------------------------

        logger.info(
            "Preparing Telegram polling..."
        )

        logger.info(
            ">>> TELEGRAM POLLING STARTING <<<"
        )

        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )


    except asyncio.CancelledError:

        logger.info(
            "Main application cancelled."
        )

        raise


    except Exception:

        logger.exception(
            "FATAL APPLICATION ERROR"
        )

        raise


    finally:

        # ----------------------------------------------------
        # Stop automatic updater
        # ----------------------------------------------------

        if updater_task is not None:

            logger.info(
                "Stopping automatic research updater..."
            )

            updater_task.cancel()

            with suppress(
                asyncio.CancelledError,
                Exception,
            ):
                await updater_task


        # ----------------------------------------------------
        # Stop HTTP server
        # ----------------------------------------------------

        if health_runner is not None:

            logger.info(
                "Stopping HTTP health server..."
            )

            with suppress(Exception):

                await stop_health_server(
                    health_runner
                )


        # ----------------------------------------------------
        # Close Telegram session
        # ----------------------------------------------------

        logger.info(
            "Closing Telegram Bot session..."
        )

        with suppress(Exception):

            await bot.session.close()


        logger.info(
            "AliDaneshYarBot stopped."
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    logger.info(
        "Python entry point detected."
    )

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        logger.info(
            "Bot stopped by keyboard interrupt."
        )

    except Exception:

        logger.exception(
            "Application exited with an error."
        )

        sys.exit(1)
