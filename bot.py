"""
Ali DaneshYar Bot
دستیار شخصی پژوهش، آموزش، تحقیق و آمادگی آزمون
Architecture:
- aiogram 3
- SQLite / aiosqlite
- Private Telegram access
- Educational content initializer
- Scientific auto updater
- HTTP health server
- Render / UptimeRobot compatible
"""
import asyncio
import logging
import sys
from contextlib import suppress
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import (
    ALLOWED_USER_IDS,
    AUTO_UPDATE_ENABLED,
    BOT_NAME,
    BOT_TOKEN,
    HOST,
    PORT,
    validate_config,
)
from database import (
    database_health_check,
    init_database,
    seed_modules,
)
from handlers.start import router as start_router
from handlers.education import router as education_router
from handlers.exams import router as exams_router
from handlers.search import router as search_router
from handlers.articles import router as articles_router
from handlers.library import router as library_router
from handlers.quiz import router as quiz_router
from handlers.flashcards import router as flashcards_router
from handlers.progress import router as progress_router
from handlers.study_plan import router as study_plan_router
from handlers.admin import router as admin_router
from services.auto_updater import auto_update_loop
from services.content_initializer import initialize_content
from web.health_server import (
    start_health_server,
    stop_health_server,
)
# ============================================================
# LOGGING
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
logger = logging.getLogger("AliDaneshYarBot")
# ============================================================
# GLOBAL TASKS
# ============================================================
health_runner = None
auto_update_task = None
# ============================================================
# STARTUP
# ============================================================
async def startup() -> tuple[Bot, Dispatcher]:
    """
    آماده‌سازی کامل ربات.
    """
    global health_runner
    global auto_update_task
    logger.info("=" * 70)
    logger.info("Starting %s", BOT_NAME)
    logger.info("=" * 70)
    # --------------------------------------------------------
    # 1. Validate configuration
    # --------------------------------------------------------
    logger.info("Validating configuration...")
    validate_config()
    logger.info(
        "Configuration validated successfully."
    )
    logger.info(
        "Allowed private users: %s",
        len(ALLOWED_USER_IDS),
    )
    # --------------------------------------------------------
    # 2. Initialize database
    # --------------------------------------------------------
    logger.info(
        "Initializing database..."
    )
    await init_database()
    logger.info(
        "Database initialized successfully."
    )
    # --------------------------------------------------------
    # 3. Seed modules
    # --------------------------------------------------------
    logger.info(
        "Seeding base modules..."
    )
    await seed_modules()
    logger.info(
        "Base modules seeded successfully."
    )
    # --------------------------------------------------------
    # 4. Import educational content
    # --------------------------------------------------------
    logger.info(
        "Initializing educational content..."
    )
    try:
        content_result = await initialize_content()
        logger.info(
            "Educational content initialization completed: %s",
            content_result,
        )
    except Exception:
        logger.exception(
            "Educational content initialization failed."
        )
        # محتوای آموزشی نباید باعث شود کل ربات از کار بیفتد.
        # بنابراین خطا ثبت می‌شود و ربات ادامه می‌دهد.
    # --------------------------------------------------------
    # 5. Database health check
    # --------------------------------------------------------
    try:
        health = await database_health_check()
        logger.info(
            "Database health: %s",
            health,
        )
    except Exception:
        logger.exception(
            "Database health check failed."
        )
    # --------------------------------------------------------
    # 6. Create Bot
    # --------------------------------------------------------
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )
    dp = Dispatcher()
    # --------------------------------------------------------
    # 7. Register routers
    # --------------------------------------------------------
    #
    # ترتیب مهم است.
    #
    # آموزش باید قبل از منوی عمومی ثبت شود.
    # --------------------------------------------------------
    logger.info(
        "Registering routers..."
    )
    dp.include_router(education_router)
    dp.include_router(start_router)
    dp.include_router(search_router)
    dp.include_router(articles_router)
    dp.include_router(exams_router)
    dp.include_router(library_router)
    dp.include_router(quiz_router)
    dp.include_router(flashcards_router)
    dp.include_router(progress_router)
    dp.include_router(study_plan_router)
    dp.include_router(admin_router)
    logger.info(
        "All routers registered."
    )
    # --------------------------------------------------------
    # 8. Start HTTP health server
    # --------------------------------------------------------
    logger.info(
        "Starting HTTP server on %s:%s",
        HOST,
        PORT,
    )
    try:
        health_runner = await start_health_server(
            host=HOST,
            port=PORT,
        )
        logger.info(
            "HTTP health server started."
        )
    except Exception:
        logger.exception(
            "Failed to start HTTP health server."
        )
        health_runner = None
    # --------------------------------------------------------
    # 9. Delete previous webhook
    # --------------------------------------------------------
    logger.info(
        "Deleting previous Telegram webhook..."
    )
    try:
        await bot.delete_webhook(
            drop_pending_updates=True
        )
        logger.info(
            "Previous webhook deleted."
        )
    except Exception:
        logger.exception(
            "Failed to delete Telegram webhook."
        )
    # --------------------------------------------------------
    # 10. Start automatic updater
    # --------------------------------------------------------
    if AUTO_UPDATE_ENABLED:
        logger.info(
            "Starting scientific auto updater..."
        )
        try:
            auto_update_task = asyncio.create_task(
                auto_update_loop()
            )
            logger.info(
                "Scientific auto updater started."
            )
        except Exception:
            logger.exception(
                "Failed to start scientific auto updater."
            )
            auto_update_task = None
    else:
        logger.info(
            "Scientific auto updater is disabled."
        )
    # --------------------------------------------------------
    # 11. Startup notification
    # --------------------------------------------------------
    await send_startup_message(bot)
    logger.info("=" * 70)
    logger.info(
        "%s is ready.",
        BOT_NAME,
    )
    logger.info("=" * 70)
    return bot, dp
# ============================================================
# STARTUP MESSAGE
# ============================================================
async def send_startup_message(
    bot: Bot,
) -> None:
    """
    ارسال پیام شروع کار برای کاربران مجاز.
    """
    if not ALLOWED_USER_IDS:
        logger.warning(
            "No allowed users configured."
        )
        return
    text = (
        "🟢 <b>علی دانش‌یار فعال شد</b>\n\n"
        "دستیار شخصی پژوهش، آموزش و آمادگی آزمون آماده است.\n\n"
        "📚 آموزش جامع\n"
        "🎯 آزمون‌های استخدامی\n"
        "🔬 تحقیق و مقالات\n"
        "🔎 جستجوی هوشمند\n"
        "📄 کتابخانه شخصی\n"
        "🧠 ابزار مطالعه\n"
        "📅 برنامه مطالعه\n"
        "⭐ ذخیره‌شده‌ها\n\n"
        "🔐 دسترسی این ربات خصوصی است."
    )
    for user_id in ALLOWED_USER_IDS:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=text,
            )
            logger.info(
                "Startup message sent to %s.",
                user_id,
            )
        except Exception:
            logger.exception(
                "Failed to send startup message to %s.",
                user_id,
            )
# ============================================================
# SHUTDOWN
# ============================================================
async def shutdown(
    bot: Bot,
) -> None:
    global health_runner
    global auto_update_task
    logger.info("=" * 70)
    logger.info(
        "Shutting down %s...",
        BOT_NAME,
    )
    logger.info("=" * 70)
    # --------------------------------------------------------
    # Stop auto updater
    # --------------------------------------------------------
    if auto_update_task is not None:
        logger.info(
            "Stopping auto updater..."
        )
        auto_update_task.cancel()
        with suppress(
            asyncio.CancelledError
        ):
            await auto_update_task
        auto_update_task = None
        logger.info(
            "Auto updater stopped."
        )
    # --------------------------------------------------------
    # Stop HTTP server
    # --------------------------------------------------------
    if health_runner is not None:
        logger.info(
            "Stopping HTTP health server..."
        )
        try:
            await stop_health_server(
                health_runner
            )
        except Exception:
            logger.exception(
                "Failed to stop HTTP health server."
            )
        health_runner = None
    # --------------------------------------------------------
    # Close Telegram session
    # --------------------------------------------------------
    if bot is not None:
        logger.info(
            "Closing Telegram session..."
        )
        try:
            await bot.session.close()
        except Exception:
            logger.exception(
                "Failed to close Telegram session."
            )
    logger.info(
        "%s stopped.",
        BOT_NAME,
    )
# ============================================================
# MAIN
# ============================================================
async def main() -> None:
    bot = None
    try:
        bot, dp = await startup()
        logger.info(
            "Starting Telegram polling..."
        )
        await dp.start_polling(
            bot,
            allowed_updates=(
                dp.resolve_used_update_types()
            ),
        )
    except KeyboardInterrupt:
        logger.info(
            "KeyboardInterrupt received."
        )
    except asyncio.CancelledError:
        logger.info(
            "Main task cancelled."
        )
    except Exception:
        logger.exception(
            "Fatal error in main process."
        )
        raise
    finally:
        if bot is not None:
            await shutdown(bot)
# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(
            "Application terminated by user."
        )
    except Exception:
        logger.exception(
            "Unhandled application error."
        )
        sys.exit(1)
