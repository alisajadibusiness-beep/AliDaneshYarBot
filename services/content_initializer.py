"""
Educational Content Initializer
علی دانش‌یار
این سرویس محتوای آموزشی موجود در فایل‌های داده را
به SQLite منتقل می‌کند.
منابع فعلی:
- data_fixed.py
- data_international_trade_FINAL.py
هدف:
Data Files
    ↓
Content Initializer
    ↓
Database
    ↓
Education Handler
    ↓
Telegram
"""
from __future__ import annotations
import inspect
import json
import logging
from typing import Any
import database
logger = logging.getLogger(
    "AliDaneshYarBot.content_initializer"
)
# ============================================================
# MODULE IDs
# ============================================================
MANAGEMENT_MODULE_ID = "management"
INTERNATIONAL_TRADE_MODULE_ID = (
    "international_business"
)
# ============================================================
# SAFE VALUE HELPERS
# ============================================================
def safe_text(
    value: Any,
    default: str = "",
) -> str:
    """
    تبدیل امن مقدار به متن.
    """
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()
def json_text(
    value: Any,
) -> str:
    """
    تبدیل ساختارهای پیچیده به JSON متنی.
    """
    if value is None:
        return ""
    if isinstance(
        value,
        (dict, list, tuple),
    ):
        try:
            return json.dumps(
                value,
                ensure_ascii=False,
            )
        except Exception:
            return str(value)
    return str(value)
def build_lesson_content(
    lesson: dict[str, Any],
) -> str:
    """
    ساخت محتوای یکپارچه Lesson.
    تمام فیلدهای آموزشی موجود در داده حفظ می‌شوند.
    """
    parts: list[str] = []
    content = safe_text(
        lesson.get("content")
    )
    if content:
        parts.append(
            f"📖 آموزش مفهومی\n\n{content}"
        )
    subtopics = lesson.get(
        "subtopics",
        [],
    )
    if subtopics:
        parts.append(
            "📌 سرفصل‌های فرعی\n\n"
            + json_text(subtopics)
        )
    specialized_tips = lesson.get(
        "specialized_tips",
        lesson.get(
            "special_points",
            [],
        ),
    )
    if specialized_tips:
        parts.append(
            "🎓 نکات تخصصی\n\n"
            + json_text(specialized_tips)
        )
    exam_tips = lesson.get(
        "exam_tips",
        [],
    )
    if exam_tips:
        parts.append(
            "🎯 نکات آزمونی\n\n"
            + json_text(exam_tips)
        )
    examples = lesson.get(
        "examples",
        lesson.get(
            "example",
            [],
        ),
    )
    if examples:
        parts.append(
            "💡 مثال\n\n"
            + json_text(examples)
        )
    review = lesson.get(
        "review",
        [],
    )
    if review:
        parts.append(
            "🔄 مرور\n\n"
            + json_text(review)
        )
    keywords = lesson.get(
        "keywords",
        [],
    )
    if keywords:
        parts.append(
            "🔑 کلیدواژه‌ها\n\n"
            + json_text(keywords)
        )
    resources = lesson.get(
        "resources",
        [],
    )
    if resources:
        parts.append(
            "📚 منابع\n\n"
            + json_text(resources)
        )
    if not parts:
        return "محتوای این درس در منبع داده موجود نیست."
    return "\n\n━━━━━━━━━━━━━━\n\n".join(
        parts
    )
# ============================================================
# DYNAMIC DATABASE CALL
# ============================================================
async def call_database_function(
    function_name: str,
    values: dict[str, Any],
) -> Any:
    """
    اجرای انعطاف‌پذیر توابع database.
    دلیل استفاده:
    ممکن است نام پارامترهای نسخه فعلی database.py
    کمی با نسخه‌ای که Content Initializer برای آن نوشته شده
    تفاوت داشته باشد.
    تابع فقط پارامترهایی را ارسال می‌کند که واقعاً
    در Signature تابع database وجود دارند.
    """
    function = getattr(
        database,
        function_name,
        None,
    )
    if function is None:
        raise RuntimeError(
            f"Database function not found: "
            f"{function_name}"
        )
    signature = inspect.signature(
        function
    )
    parameters = signature.parameters
    kwargs: dict[str, Any] = {}
    aliases = {
        "module_id": [
            "module_id",
            "module",
        ],
        "lesson_id": [
            "lesson_id",
            "lesson",
        ],
        "title": [
            "title",
            "name",
        ],
        "content": [
            "content",
            "text",
            "body",
        ],
        "question": [
            "question",
            "text",
            "question_text",
        ],
        "options": [
            "options",
            "choices",
        ],
        "answer": [
            "answer",
            "correct_answer",
            "correct",
        ],
        "explanation": [
            "explanation",
            "solution",
        ],
    }
    for source_key, names in aliases.items():
        if source_key not in values:
            continue
        value = values[
            source_key
        ]
        for name in names:
            if name in parameters:
                kwargs[name] = value
                break
    # --------------------------------------------------------
    # Call function
    # --------------------------------------------------------
    result = function(
        **kwargs
    )
    if inspect.isawaitable(result):
        return await result
    return result
# ============================================================
# FIND MODULE
# ============================================================
async def ensure_module(
    module_id: str,
    title: str,
    description: str = "",
) -> Any:
    """
    اطمینان از وجود Module.
    ابتدا ماژول‌های موجود را بررسی می‌کند.
    """
    try:
        modules = await database.get_modules()
        for module in modules:
            if str(
                module.get("id", "")
            ) == module_id:
                return module
            if str(
                module.get("module_id", "")
            ) == module_id:
                return module
    except Exception:
        logger.exception(
            "Could not inspect existing modules."
        )
    # اگر ماژول قبلاً توسط seed_modules ایجاد شده،
    # معمولاً همین بخش اجرا نمی‌شود.
    #
    # تلاش برای ایجاد در صورت وجود تابع مناسب.
    for function_name in (
        "add_module",
        "create_module",
    ):
        if not hasattr(
            database,
            function_name,
        ):
            continue
        try:
            return await call_database_function(
                function_name,
                {
                    "module_id": module_id,
                    "title": title,
                    "content": description,
                },
            )
        except Exception:
            logger.exception(
                "Failed to create module using %s.",
                function_name,
            )
    return None
# ============================================================
# EXISTING LESSON CHECK
# ============================================================
async def find_existing_lesson(
    module_id: str,
    title: str,
) -> Any | None:
    """
    جلوگیری از ایجاد مجدد Lesson.
    """
    try:
        lessons = await database.get_lessons(
            module_id
        )
    except Exception:
        logger.exception(
            "Could not retrieve lessons for %s.",
            module_id,
        )
        return None
    normalized = safe_text(
        title
    ).casefold()
    for lesson in lessons:
        existing_title = safe_text(
            lesson.get("title")
        ).casefold()
        if existing_title == normalized:
            return lesson
    return None
# ============================================================
# EXISTING QUESTION CHECK
# ============================================================
async def question_exists(
    lesson_id: Any,
    question_text: str,
) -> bool:
    """
    بررسی سؤال تکراری.
    """
    try:
        questions = await database.get_questions(
            lesson_id=lesson_id,
            limit=500,
        )
    except Exception:
        logger.exception(
            "Could not retrieve lesson questions."
        )
        return False
    normalized = safe_text(
        question_text
    ).casefold()
    for question in questions:
        existing = safe_text(
            question.get(
                "question",
                question.get(
                    "text",
                    "",
                ),
            )
        ).casefold()
        if existing == normalized:
            return True
    return False
# ============================================================
# IMPORT LESSON
# ============================================================
async def import_lesson(
    module_id: str,
    lesson: dict[str, Any],
) -> tuple[Any, int]:
    """
    Import یک Lesson و Questions آن.
    Returns:
        lesson_record, question_count
    """
    title = safe_text(
        lesson.get(
            "title",
            lesson.get(
                "id",
                "درس بدون عنوان",
            ),
        )
    )
    content = build_lesson_content(
        lesson
    )
    existing = await find_existing_lesson(
        module_id,
        title,
    )
    if existing is not None:
        lesson_record = existing
        lesson_db_id = existing.get(
            "id"
        )
    else:
        lesson_record = (
            await call_database_function(
                "add_lesson",
                {
                    "module_id": module_id,
                    "title": title,
                    "content": content,
                },
            )
        )
        lesson_db_id = None
        if isinstance(
            lesson_record,
            dict,
        ):
            lesson_db_id = (
                lesson_record.get("id")
            )
        elif isinstance(
            lesson_record,
            (int, str),
        ):
            lesson_db_id = lesson_record
    # --------------------------------------------------------
    # If DB did not return an ID,
    # find it again by title.
    # --------------------------------------------------------
    if lesson_db_id is None:
        refreshed = (
            await find_existing_lesson(
                module_id,
                title,
            )
        )
        if refreshed is not None:
            lesson_record = refreshed
            lesson_db_id = (
                refreshed.get("id")
            )
    if lesson_db_id is None:
        raise RuntimeError(
            f"Could not determine database ID "
            f"for lesson: {title}"
        )
    # --------------------------------------------------------
    # Questions
    # --------------------------------------------------------
    quiz = lesson.get(
        "quiz",
        [],
    )
    if not isinstance(
        quiz,
        list,
    ):
        quiz = []
    question_count = 0
    for question in quiz:
        if not isinstance(
            question,
            dict,
        ):
            continue
        question_text = safe_text(
            question.get(
                "question",
                question.get(
                    "text",
                    "",
                ),
            )
        )
        if not question_text:
            continue
        if await question_exists(
            lesson_db_id,
            question_text,
        ):
            continue
        options = question.get(
            "options",
            [],
        )
        if isinstance(
            options,
            list,
        ):
            normalized_options = []
            for option in options:
                if isinstance(
                    option,
                    dict,
                ):
                    option_id = safe_text(
                        option.get("id")
                    )
                    option_text = safe_text(
                        option.get("text")
                    )
                    normalized_options.append(
                        {
                            "id": option_id,
                            "text": option_text,
                        }
                    )
                else:
                    normalized_options.append(
                        {
                            "id": "",
                            "text": safe_text(
                                option
                            ),
                        }
                    )
            options = normalized_options
        answer = safe_text(
            question.get(
                "correct_answer",
                question.get(
                    "answer",
                    "",
                ),
            )
        )
        explanation = safe_text(
            question.get(
                "explanation",
                "",
            )
        )
        try:
            await call_database_function(
                "add_question",
                {
                    "module_id": module_id,
                    "lesson_id": lesson_db_id,
                    "question": question_text,
                    "options": json_text(
                        options
                    ),
                    "answer": answer,
                    "explanation": explanation,
                },
            )
            question_count += 1
        except Exception:
            logger.exception(
                "Failed to import question: %s",
                question_text[:80],
            )
    return (
        lesson_record,
        question_count,
    )
# ============================================================
# MANAGEMENT IMPORT
# ============================================================
async def import_management() -> dict[str, int]:
    """
    وارد کردن محتوای مدیریت.
    """
    try:
        from data_fixed import (
            MANAGEMENT_CHAPTERS,
        )
    except Exception:
        logger.exception(
            "Could not import data_fixed.py."
        )
        return {
            "chapters": 0,
            "lessons": 0,
            "questions": 0,
        }
    await ensure_module(
        MANAGEMENT_MODULE_ID,
        "مدیریت و بازرگانی",
        "آموزش جامع مدیریت و بازرگانی.",
    )
    chapters = 0
    lessons = 0
    questions = 0
    for chapter in MANAGEMENT_CHAPTERS:
        if not isinstance(
            chapter,
            dict,
        ):
            continue
        # فقط فصل‌های مربوط به مدیریت.
        # فایل data_fixed.py ممکن است داده‌های سازگاری
        # تجارت بین‌الملل را هم در خود داشته باشد.
        chapter_id = safe_text(
            chapter.get("id")
        )
        chapter_title = safe_text(
            chapter.get("title")
        )
        if not chapter_id:
            continue
        # فصل
        chapters += 1
        chapter_lessons = chapter.get(
            "lessons",
            [],
        )
        if not isinstance(
            chapter_lessons,
            list,
        ):
            continue
        for lesson in chapter_lessons:
            if not isinstance(
                lesson,
                dict,
            ):
                continue
            # جلوگیری از وارد کردن دوباره
            # داده تجارت بین‌الملل که در
            # data_fixed به compatibility اضافه شده.
            lesson_id = safe_text(
                lesson.get("id")
            )
            if lesson_id.startswith(
                "it_"
            ):
                continue
            try:
                _, count = await import_lesson(
                    MANAGEMENT_MODULE_ID,
                    lesson,
                )
                lessons += 1
                questions += count
            except Exception:
                logger.exception(
                    "Failed to import management lesson: %s",
                    lesson.get("title"),
                )
    return {
        "chapters": chapters,
        "lessons": lessons,
        "questions": questions,
    }
# ============================================================
# INTERNATIONAL TRADE IMPORT
# ============================================================
async def import_international_trade() -> dict[str, int]:
    """
    وارد کردن تجارت بین‌الملل.
    """
    try:
        import data_international_trade_FINAL as trade
    except Exception:
        logger.exception(
            "Could not import data_international_trade_FINAL.py."
        )
        return {
            "chapters": 0,
            "lessons": 0,
            "questions": 0,
        }
    await ensure_module(
        INTERNATIONAL_TRADE_MODULE_ID,
        "تجارت بین‌الملل",
        "آموزش جامع تجارت بین‌الملل.",
    )
    chapters = 0
    lessons = 0
    questions = 0
    chapter_list = trade.get_chapters()
    for chapter in chapter_list:
        if not isinstance(
            chapter,
            dict,
        ):
            continue
        chapter_id = safe_text(
            chapter.get("id")
        )
        if not chapter_id:
            continue
        chapters += 1
        lesson_list = trade.get_lessons(
            chapter_id
        )
        for lesson in lesson_list:
            if not isinstance(
                lesson,
                dict,
            ):
                continue
            lesson_copy = dict(
                lesson
            )
            # API سوال‌ها جدا از Lesson نگهداری می‌شود.
            quiz = trade.get_quiz_questions(
                chapter_id,
                safe_text(
                    lesson.get("id")
                ),
            )
            lesson_copy["quiz"] = quiz
            try:
                _, count = await import_lesson(
                    INTERNATIONAL_TRADE_MODULE_ID,
                    lesson_copy,
                )
                lessons += 1
                questions += count
            except Exception:
                logger.exception(
                    "Failed to import trade lesson: %s",
                    lesson.get("title"),
                )
    return {
        "chapters": chapters,
        "lessons": lessons,
        "questions": questions,
    }
# ============================================================
# MAIN INITIALIZER
# ============================================================
async def initialize_content() -> dict[str, Any]:
    """
    اجرای کامل Content Initializer.
    """
    logger.info(
        "=========================================="
    )
    logger.info(
        "Educational Content Initializer"
    )
    logger.info(
        "=========================================="
    )
    management = (
        await import_management()
    )
    logger.info(
        "Management import: %s",
        management,
    )
    international_trade = (
        await import_international_trade()
    )
    logger.info(
        "International Trade import: %s",
        international_trade,
    )
    result = {
        "management": management,
        "international_trade": international_trade,
        "total_lessons": (
            management["lessons"]
            + international_trade["lessons"]
        ),
        "total_questions": (
            management["questions"]
            + international_trade["questions"]
        ),
    }
    logger.info(
        "Content initialization result: %s",
        result,
    )
    return result
# ============================================================
# CLI
# ============================================================
async def main() -> None:
    await database.init_database()
    await database.seed_modules()
    result = await initialize_content()
    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )
if __name__ == "__main__":
    import asyncio
    asyncio.run(
        main()
    )
