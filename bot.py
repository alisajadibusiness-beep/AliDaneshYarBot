"""
Ali DaneshYar Bot
دستیار شخصی پژوهش، آموزش، تحقیق و آمادگی آزمون
ویژگی‌های اصلی:
- Telegram Bot با aiogram 3
- دسترسی خصوصی بر اساس ALLOWED_USER_IDS
- SQLite + aiosqlite
- ماژول‌های آموزشی
- آزمون‌های استخدامی
- مقالات و منابع علمی
- جستجوی هوشمند
- کتابخانه شخصی
- فلش‌کارت
- آزمون و ثبت پیشرفت
- برنامه مطالعه
- Auto Updater
- HTTP Health Server برای Render / UptimeRobot
نکته:
ترتیب Routerها مهم است.
Router آموزش قبل از Router منوی اصلی ثبت می‌شود تا
هندلرهای تخصصی آموزش توسط fallbackهای عمومی گرفته نشوند.
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
    BOT_NAME,
    BOT_TOKEN,
    HOST,
    PORT,
    AUTO_UPDATE_ENABLED,
    validate_config,
)
from database import (
    init_database,
    seed_modules,
    database_health_check,
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
)
logger = logging.getLogger("AliDaneshYarBot")
# ============================================================
# GLOBAL STATE
# ============================================================
health_runner = None
auto_update_task = None
# ============================================================
# STARTUP
# ============================================================
async def startup() -> tuple[Bot, Dispatcher]:
    """
    آماده‌سازی کامل ربات:
    1. اعتبارسنجی تنظیمات
    2. ساخت دیتابیس
    3. Seed ماژول‌ها
    4. ساخت Bot و Dispatcher
    5. ثبت Routerها
    6. راه‌اندازی Health Server
    7. حذف Webhook قبلی
    8. راه‌اندازی Auto Updater
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
        "Private allowed users: %s",
        len(ALLOWED_USER_IDS),
    )
    # --------------------------------------------------------
    # 2. Initialize database
    # --------------------------------------------------------
    logger.info("Initializing database...")
    await init_database()
    logger.info(
        "Database initialized successfully."
    )
    # --------------------------------------------------------
    # 3. Seed educational modules
    # --------------------------------------------------------
    logger.info("Seeding educational modules...")
    await seed_modules()
    logger.info(
        "Educational modules seeded successfully."
    )
    # --------------------------------------------------------
    # 4. Database health check
    # --------------------------------------------------------
    try:
        db_health = await database_health_check()
        logger.info(
            "Database health check: %s",
            db_health,
        )
    except Exception:
        logger.exception(
            "Database health check failed."
        )
    # --------------------------------------------------------
    # 5. Create Telegram Bot
    # --------------------------------------------------------
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )
    dp = Dispatcher()
    # --------------------------------------------------------
    # 6. Register Routers
    # --------------------------------------------------------
    #
    # ترتیب بسیار مهم است.
    #
    # education_router باید قبل از start_router باشد،
    # چون start.py شامل بعضی هندلرهای منوی عمومی و fallback است.
    #
    # ترتیب فعلی:
    #
    # 1. Education
    # 2. Start / Main Menu
    # 3. Search
    # 4. Articles
    # 5. Exams
    # 6. Library
    # 7. Quiz
    # 8. Flashcards
    # 9. Progress
    # 10. Study Plan
    # 11. Admin
    #
    # --------------------------------------------------------
    logger.info("Registering routers...")
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
        "All routers registered successfully."
    )
    # --------------------------------------------------------
    # 7. Start HTTP Health Server
    # --------------------------------------------------------
    logger.info(
        "Starting HTTP health server on %s:%s",
        HOST,
        PORT,
    )
    try:
        health_runner = await start_health_server(
            host=HOST,
            port=PORT,
        )
        logger.info(
            "Health server started successfully."
        )
    except Exception:
        logger.exception(
            "Failed to start HTTP health server."
        )
        # اگر Health Server بالا نیاید،
        # ربات Telegram همچنان می‌تواند اجرا شود.
        health_runner = None
    # --------------------------------------------------------
    # 8. Delete previous webhook
    # --------------------------------------------------------
    logger.info(
        "Removing previous Telegram webhook..."
    )
    try:
        await bot.delete_webhook(
            drop_pending_updates=True
        )
        logger.info(
            "Previous webhook removed successfully."
        )
    except Exception:
        logger.exception(
            "Failed to remove previous webhook."
        )
    # --------------------------------------------------------
    # 9. Start Auto Updater
    # --------------------------------------------------------
    if AUTO_UPDATE_ENABLED:
        logger.info(
            "Starting automatic scientific resource updater..."
        )
        try:
            auto_update_task = asyncio.create_task(
                auto_update_loop()
            )
            logger.info(
                "Auto updater started successfully."
            )
        except Exception:
            logger.exception(
                "Failed to start auto updater."
            )
            auto_update_task = None
    else:
        logger.info(
            "Automatic resource updater is disabled."
        )
    # --------------------------------------------------------
    # 10. Send startup notification
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
async def send_startup_message(bot: Bot) -> None:
    """
    ارسال پیام شروع به کار به کاربر مجاز.
    """
    if not ALLOWED_USER_IDS:
        logger.warning(
            "No allowed users configured."
        )
        return
    startup_text = (
        "🟢 <b>علی دانش‌یار فعال شد</b>\n\n"
        "دستیار شخصی پژوهش، آموزش و آمادگی آزمون آماده است.\n\n"
        "📚 آموزش جامع\n"
        "🎯 آزمون‌های استخدامی\n"
        "🔬 تحقیق و مقالات\n"
        "🔎 جستجوی هوشمند\n"
        "📄 کتابخانه شخصی\n"
        "🧠 ابزار مطالعه\n"
        "📅 برنامه مطالعه\n\n"
        "🔐 دسترسی این ربات خصوصی است."
    )
    for user_id in ALLOWED_USER_IDS:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=startup_text,
            )
            logger.info(
                "Startup message sent to user %s.",
                user_id,
            )
        except Exception:
            logger.exception(
                "Failed to send startup message to user %s.",
                user_id,
            )
# ============================================================
# SHUTDOWN
# ============================================================
async def shutdown(bot: Bot) -> None:
    """
    خاموش‌سازی تمیز ربات.
    """
    global health_runner
    global auto_update_task
    logger.info("=" * 70)
    logger.info("Shutting down %s...", BOT_NAME)
    logger.info("=" * 70)
    # --------------------------------------------------------
    # Stop Auto Updater
    # --------------------------------------------------------
    if auto_update_task is not None:
        logger.info(
            "Stopping auto updater..."
        )
        auto_update_task.cancel()
        with suppress(asyncio.CancelledError):
            await auto_update_task
        auto_update_task = None
        logger.info(
            "Auto updater stopped."
        )
    # --------------------------------------------------------
    # Stop Health Server
    # --------------------------------------------------------
    if health_runner is not None:
        logger.info(
            "Stopping health server..."
        )
        try:
            await stop_health_server(
                health_runner
            )
        except Exception:
            logger.exception(
                "Error while stopping health server."
            )
        health_runner = None
    # --------------------------------------------------------
    # Close Telegram session
    # --------------------------------------------------------
    if bot is not None:
        logger.info(
            "Closing Telegram bot session..."
        )
        try:
            await bot.session.close()
        except Exception:
            logger.exception(
                "Error while closing Telegram session."
            )
    logger.info(
        "%s stopped.",
        BOT_NAME,
    )
# ============================================================
# MAIN
# ============================================================
async def main() -> None:
    """
    نقطه ورود اصلی برنامه.
    """
    bot = None
    try:
        # ----------------------------------------------------
        # Startup
        # ----------------------------------------------------
        bot, dp = await startup()
        # ----------------------------------------------------
        # Start polling
        # ----------------------------------------------------
        logger.info(
            "Starting Telegram polling..."
        )
        logger.info(
            "Bot is now listening for updates."
        )
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
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
# PYTHON ENTRY POINT
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
            "Application terminated because of an unhandled error."
        )
        sys.exit(1)
