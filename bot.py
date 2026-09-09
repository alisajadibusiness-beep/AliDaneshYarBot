import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from config import (
    BOT_TOKEN,
    ALLOWED_USER_IDS,
    TOPICS,
)
from database import init_database, seed_modules

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

from services.auto_updater import auto_update_loop


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("AliDaneshYarBot")


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is not configured."
        )

    if not ALLOWED_USER_IDS:
        raise RuntimeError(
            "ALLOWED_USER_IDS is not configured."
        )

    logger.info("Starting AliDaneshYarBot...")

    await init_database()
    await seed_modules(TOPICS)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

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

    updater_task = asyncio.create_task(
        auto_update_loop(bot)
    )

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )

    finally:
        updater_task.cancel()

        try:
            await updater_task
        except asyncio.CancelledError:
            pass

        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
