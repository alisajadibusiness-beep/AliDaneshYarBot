import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher

from config import (
    BOT_TOKEN,
    ALLOWED_USER_IDS,
    EDUCATIONAL_MODULES,
    PORT,
    HOST,
    validate_config,
    get_config_summary,
)

from database import (
    init_database,
    seed_modules,
)

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

from services.auto_updater import (
    auto_update_loop,
)

from web.health_server import (
    start_health_server,
    stop_health_server,
)


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(
    "AliDaneshYarBot"
)


# ============================================================
# Main application
# ============================================================

async def main() -> None:

    # --------------------------------------------------------
    # Validate configuration
    # --------------------------------------------------------

    validate_config()

    logger.info(
        "Starting %s...",
        get_config_summary()["app_name"],
    )

    logger.info(
        "Allowed users: %s",
        len(ALLOWED_USER_IDS),
    )

    logger.info(
        "HTTP server: %s:%s",
        HOST,
        PORT,
    )


    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    logger.info(
        "Initializing database..."
    )

    await init_database()

    logger.info(
        "Database initialized."
    )


    # --------------------------------------------------------
    # Seed educational modules
    # --------------------------------------------------------

    logger.info(
        "Seeding educational modules..."
    )

    await seed_modules(
        EDUCATIONAL_MODULES
    )

    logger.info(
        "Educational modules initialized."
    )


    # --------------------------------------------------------
    # Telegram Bot
    # --------------------------------------------------------

    bot = Bot(
        token=BOT_TOKEN,
    )

    dp = Dispatcher()


    # --------------------------------------------------------
    # Register routers
    # --------------------------------------------------------

    dp.include_router(
        start_router
    )

    dp.include_router(
        search_router
    )

    dp.include_router(
        education_router
    )

    dp.include_router(
        exams_router
    )

    dp.include_router(
        articles_router
    )

    dp.include_router(
        library_router
    )

    dp.include_router(
        quiz_router
    )

    dp.include_router(
        flashcards_router
    )

    dp.include_router(
        progress_router
    )

    dp.include_router(
        study_plan_router
    )

    dp.include_router(
        admin_router
    )


    # --------------------------------------------------------
    # Start HTTP server for Render
    # --------------------------------------------------------

    health_runner = None

    try:

        health_runner = await start_health_server(
            host=HOST,
            port=PORT,
        )

        logger.info(
            "Render HTTP server is ready."
        )

        logger.info(
            "Health endpoint: /health"
        )


        # ----------------------------------------------------
        # Remove previous Telegram webhook
        # ----------------------------------------------------

        try:

            await bot.delete_webhook(
                drop_pending_updates=True
            )

            logger.info(
                "Telegram webhook removed. "
                "Polling mode is ready."
            )

        except Exception:

            logger.exception(
                "Could not delete Telegram webhook."
            )


        # ----------------------------------------------------
        # Start automatic research updater
        # ----------------------------------------------------

        updater_task = asyncio.create_task(
            auto_update_loop(bot)
        )

        logger.info(
            "Automatic research updater started."
        )


        # ----------------------------------------------------
        # Start Telegram polling
        # ----------------------------------------------------

        logger.info(
            "Starting Telegram polling..."
        )

        await dp.start_polling(
            bot,
            allowed_updates=(
                dp.resolve_used_update_types()
            ),
        )


    except asyncio.CancelledError:

        logger.info(
            "Main application cancelled."
        )

        raise


    except Exception:

        logger.exception(
            "Fatal application error."
        )

        raise


    finally:

        # ----------------------------------------------------
        # Stop updater
        # ----------------------------------------------------

        try:

            if (
                "updater_task" in locals()
                and updater_task
            ):

                updater_task.cancel()

                try:

                    await updater_task

                except asyncio.CancelledError:

                    pass

        except Exception:

            logger.exception(
                "Error while stopping updater."
            )


        # ----------------------------------------------------
        # Stop HTTP server
        # ----------------------------------------------------

        try:

            await stop_health_server(
                health_runner
            )

        except Exception:

            logger.exception(
                "Error while stopping health server."
            )


        # ----------------------------------------------------
        # Close Telegram session
        # ----------------------------------------------------

        try:

            await bot.session.close()

        except Exception:

            logger.exception(
                "Error while closing Telegram session."
            )


        logger.info(
            "AliDaneshYarBot stopped."
        )


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":

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
