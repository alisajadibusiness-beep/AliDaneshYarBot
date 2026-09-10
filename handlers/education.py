"""
AliDaneshYarBot
handlers/education.py
Real educational system.
Features:
- Educational modules
- Lessons
- Lesson content
- Progress tracking
- Bookmarks
- Flashcards
- Lesson quizzes
- Quiz results
- Weak-topic tracking
- Navigation
- Private-user protection
Data source:
SQLite database through database.py
Important:
The database must contain lessons/questions.
seed_modules() only creates module records.
Lesson/question content must be initialized separately.
"""
from __future__ import annotations
import json
import logging
from typing import Any
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from config import ALLOWED_USER_IDS
from database import (
    get_modules,
    get_module,
    get_lessons,
    get_lesson,
    get_questions,
    save_progress,
    save_quiz_result,
    save_bookmark,
    add_flashcard,
    get_flashcards,
    update_weak_topic,
)
logger = logging.getLogger("AliDaneshYarBot.education")
router = Router(name="education")
# ============================================================
# CONSTANTS
# ============================================================
EDUCATION_MENU = "📚 آموزش جامع"
MAIN_MENU = "🏠 منوی اصلی"
MODULE_PREFIX = "edu_module:"
LESSON_PREFIX = "edu_lesson:"
START_LESSON_PREFIX = "edu_start:"
CONTENT_PREFIX = "edu_content:"
FLASHCARD_PREFIX = "edu_flash:"
QUIZ_PREFIX = "edu_quiz:"
ANSWER_PREFIX = "edu_answer:"
BOOKMARK_PREFIX = "edu_bookmark:"
BACK_MODULES = "edu_modules"
BACK_LESSONS_PREFIX = "edu_lessons:"
BACK_LESSON_PREFIX = "edu_back_lesson:"
QUIZ_RESULT_PREFIX = "edu_quiz_result:"
# ============================================================
# ACCESS
# ============================================================
def is_allowed(user_id: int | None) -> bool:
    if user_id is None:
        return False
    return user_id in ALLOWED_USER_IDS
async def deny(message: Message) -> None:
    await message.answer(
        "⛔ دسترسی به این ربات خصوصی است."
    )
# ============================================================
# KEYBOARDS
# ============================================================
def modules_keyboard(
    modules: list[dict[str, Any]],
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for module in modules:
        module_id = module.get("id")
        title = str(
            module.get("title")
            or module.get("module_key")
            or "بدون عنوان"
        )
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"📘 {title}",
                    callback_data=f"{MODULE_PREFIX}{module_id}",
                )
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text=MAIN_MENU,
                callback_data="edu_main_menu",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
def lessons_keyboard(
    module_id: int,
    lessons: list[dict[str, Any]],
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for index, lesson in enumerate(lessons, 1):
        lesson_id = lesson.get("id")
        title = str(
            lesson.get("title")
            or f"درس {index}"
        )
        chapter = str(
            lesson.get("chapter")
            or ""
        ).strip()
        if chapter:
            button_text = f"📖 {index}. {title}"
        else:
            button_text = f"📖 {index}. {title}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=button_text[:64],
                    callback_data=f"{LESSON_PREFIX}{lesson_id}",
                )
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text="⬅️ بازگشت به ماژول‌ها",
                callback_data=BACK_MODULES,
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
def lesson_keyboard(
    lesson_id: int,
    module_id: int | None,
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text="📖 شروع / ادامه درس",
                callback_data=f"{START_LESSON_PREFIX}{lesson_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text="🃏 فلش‌کارت",
                callback_data=f"{FLASHCARD_PREFIX}{lesson_id}",
            ),
            InlineKeyboardButton(
                text="🧠 آزمون درس",
                callback_data=f"{QUIZ_PREFIX}{lesson_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⭐ ذخیره درس",
                callback_data=f"{BOOKMARK_PREFIX}{lesson_id}",
            )
        ],
    ]
    if module_id is not None:
        rows.append(
            [
                InlineKeyboardButton(
                    text="⬅️ بازگشت به درس‌ها",
                    callback_data=f"{BACK_LESSONS_PREFIX}{module_id}",
                )
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text=MAIN_MENU,
                callback_data="edu_main_menu",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
def content_keyboard(
    lesson_id: int,
    module_id: int | None,
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text="🃏 فلش‌کارت درس",
                callback_data=f"{FLASHCARD_PREFIX}{lesson_id}",
            ),
            InlineKeyboardButton(
                text="🧠 آزمون درس",
                callback_data=f"{QUIZ_PREFIX}{lesson_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⭐ ذخیره درس",
                callback_data=f"{BOOKMARK_PREFIX}{lesson_id}",
            )
        ],
    ]
    if module_id is not None:
        rows.append(
            [
                InlineKeyboardButton(
                    text="⬅️ بازگشت به درس",
                    callback_data=f"{BACK_LESSON_PREFIX}{lesson_id}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)
def quiz_question_keyboard(
    lesson_id: int,
    question_id: int,
    options: list[Any],
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for index, option in enumerate(options):
        if isinstance(option, dict):
            label = (
                option.get("text")
                or option.get("label")
                or option.get("title")
                or option.get("value")
                or str(option)
            )
            value = (
                option.get("key")
                or option.get("id")
                or option.get("value")
                or str(index + 1)
            )
        else:
            label = str(option)
            value = str(index + 1)
        rows.append(
            [
                InlineKeyboardButton(
                    text=str(label)[:60],
                    callback_data=(
                        f"{ANSWER_PREFIX}"
                        f"{lesson_id}:"
                        f"{question_id}:"
                        f"{value}"
                    ),
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)
# ============================================================
# HELPERS
# ============================================================
def parse_options(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return list(value.values())
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                return list(parsed.values())
        except Exception:
            pass
        lines = [
            line.strip()
            for line in value.splitlines()
            if line.strip()
        ]
        return lines
    return [str(value)]
def normalize_answer(
    value: Any,
) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    replacements = {
        "الف": "A",
        "الف)": "A",
        "ب": "B",
        "ب)": "B",
        "پ": "C",
        "پ)": "C",
        "ج": "C",
        "ج)": "C",
        "د": "D",
        "د)": "D",
    }
    return replacements.get(
        text,
        text,
    ).strip().lower()
def truncate_text(
    text: str,
    limit: int = 3900,
) -> str:
    text = str(text or "")
    if len(text) <= limit:
        return text
    return (
        text[:limit - 80]
        + "\n\n"
        "📌 ادامه این درس در بخش بعدی نمایش داده می‌شود."
    )
def lesson_module_id(
    lesson: dict[str, Any],
) -> int | None:
    value = lesson.get("module_id")
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
def format_lesson_header(
    lesson: dict[str, Any],
) -> str:
    title = str(
        lesson.get("title")
        or "درس بدون عنوان"
    )
    chapter = str(
        lesson.get("chapter")
        or ""
    ).strip()
    level = str(
        lesson.get("level")
        or ""
    ).strip()
    parts = [
        f"📖 <b>{title}</b>"
    ]
    if chapter:
        parts.append(
            f"📚 فصل: {chapter}"
        )
    if level:
        parts.append(
            f"🎚 سطح: {level}"
        )
    return "\n".join(parts)
def build_lesson_text(
    lesson: dict[str, Any],
) -> str:
    title = str(
        lesson.get("title")
        or "درس بدون عنوان"
    )
    description = str(
        lesson.get("description")
        or ""
    ).strip()
    content = str(
        lesson.get("content")
        or ""
    ).strip()
    keywords = lesson.get("keywords")
    text_parts: list[str] = [
        f"📖 <b>{title}</b>"
    ]
    if description:
        text_parts.extend(
            [
                "",
                "🎯 <b>هدف و معرفی درس</b>",
                description,
            ]
        )
    if content:
        text_parts.extend(
            [
                "",
                "📚 <b>آموزش</b>",
                content,
            ]
        )
    else:
        text_parts.extend(
            [
                "",
                "⚠️ برای این درس هنوز محتوای آموزشی ثبت نشده است.",
            ]
        )
    if keywords:
        if isinstance(keywords, str):
            try:
                parsed_keywords = json.loads(keywords)
                if isinstance(parsed_keywords, list):
                    keywords_text = "، ".join(
                        str(item)
                        for item in parsed_keywords
                    )
                else:
                    keywords_text = keywords
            except Exception:
                keywords_text = keywords
        elif isinstance(keywords, list):
            keywords_text = "، ".join(
                str(item)
                for item in keywords
            )
        else:
            keywords_text = str(keywords)
        if keywords_text.strip():
            text_parts.extend(
                [
                    "",
                    "🔑 <b>واژگان کلیدی</b>",
                    keywords_text,
                ]
            )
    return "\n".join(text_parts)
# ============================================================
# MAIN EDUCATION MENU
# ============================================================
@router.message(F.text == EDUCATION_MENU)
async def education_menu(
    message: Message,
):
    if not is_allowed(
        message.from_user.id
        if message.from_user
        else None
    ):
        await deny(message)
        return
    modules = await get_modules()
    if not modules:
        await message.answer(
            "📚 <b>آموزش جامع</b>\n\n"
            "هنوز هیچ ماژول آموزشی در دیتابیس ثبت نشده است."
        )
        return
    text = (
        "📚 <b>آموزش جامع</b>\n\n"
        "رشته و حوزه موردنظر را انتخاب کن:\n\n"
        "هر ماژول می‌تواند شامل فصل‌ها، درس‌ها، "
        "فلش‌کارت و آزمون اختصاصی باشد."
    )
    await message.answer(
        text,
        reply_markup=modules_keyboard(modules),
        parse_mode="HTML",
    )
# ============================================================
# MODULE
# ============================================================
@router.callback_query(
    F.data.startswith(MODULE_PREFIX)
)
async def module_handler(
    callback: CallbackQuery,
):
    if not is_allowed(
        callback.from_user.id
    ):
        await callback.answer(
            "⛔ دسترسی غیرمجاز",
            show_alert=True,
        )
        return
    try:
        module_id = int(
            callback.data.split(":", 1)[1]
        )
    except Exception:
        await callback.answer(
            "شناسه ماژول نامعتبر است.",
            show_alert=True,
        )
        return
    module = None
    modules = await get_modules()
    for item in modules:
        if int(item["id"]) == module_id:
            module = item
            break
    if module is None:
        await callback.answer(
            "ماژول پیدا نشد.",
            show_alert=True,
        )
        return
    lessons = await get_lessons(
        module_id
    )
    title = str(
        module.get("title")
        or "ماژول آموزشی"
    )
    description = str(
        module.get("description")
        or ""
    ).strip()
    if not lessons:
        text = (
            f"📘 <b>{title}</b>\n\n"
            "هنوز هیچ درسی برای این ماژول ثبت نشده است.\n\n"
            "ساختار آماده است و بعد از ورود محتوای "
            "آموزشی، درس‌ها در همین بخش نمایش داده می‌شوند."
        )
        if description:
            text += (
                f"\n\n📝 {description}"
            )
        await callback.message.edit_text(
            text,
            reply_markup=lessons_keyboard(
                module_id,
                [],
            ),
            parse_mode="HTML",
        )
        await callback.answer()
        return
    text = (
        f"📘 <b>{title}</b>\n\n"
    )
    if description:
        text += (
            f"{description}\n\n"
        )
    text += (
        f"📚 تعداد درس‌ها: <b>{len(lessons)}</b>\n\n"
        "درس موردنظر را انتخاب کن:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=lessons_keyboard(
            module_id,
            lessons,
        ),
        parse_mode="HTML",
    )
    await callback.answer()
# ============================================================
# LESSON LIST
# ============================================================
@router.callback_query(
    F.data.startswith(BACK_LESSONS_PREFIX)
)
async def back_to_lessons(
    callback: CallbackQuery,
):
    if not is_allowed(
        callback.from_user.id
    ):
        await callback.answer(
            "⛔ دسترسی غیرمجاز",
            show_alert=True,
        )
        return
    try:
        module_id = int(
            callback.data.split(":", 1)[1]
        )
    except Exception:
        await callback.answer(
            "شناسه نامعتبر است.",
            show_alert=True,
        )
        return
    module = None
    modules = await get_modules()
    for item in modules:
        if int(item["id"]) == module_id:
            module = item
            break
    if module is None:
        await callback.answer(
            "ماژول پیدا نشد.",
            show_alert=True,
        )
        return
    lessons = await get_lessons(
        module_id
    )
    title = str(
        module.get("title")
        or "ماژول آموزشی"
    )
    await callback.message.edit_text(
        f"📘 <b>{title}</b>\n\n"
        f"📚 تعداد درس‌ها: <b>{len(lessons)}</b>\n\n"
        "درس موردنظر را انتخاب کن:",
        reply_markup=lessons_keyboard(
            module_id,
            lessons,
        ),
        parse_mode="HTML",
    )
    await callback.answer()
# ============================================================
# LESSON
# ============================================================
@router.callback_query(
    F.data.startswith(LESSON_PREFIX)
)
async def lesson_handler(
    callback: CallbackQuery,
):
    if not is_allowed(
        callback.from_user.id
    ):
        await callback.answer(
            "⛔ دسترسی غیرمجاز",
            show_alert=True,
        )
        return
    try:
        lesson_id = int(
            callback.data.split(":", 1)[1]
        )
    except Exception:
        await callback.answer(
            "شناسه درس نامعتبر است.",
            show_alert=True,
        )
        return
    lesson = await get_lesson(
        lesson_id
    )
    if not lesson:
        await callback.answer(
            "درس پیدا نشد.",
            show_alert=True,
        )
        return
    module_id = lesson_module_id(
        lesson
    )
    title = str(
        lesson.get("title")
        or "درس"
    )
    text = (
        f"📖 <b>{title}</b>\n\n"
        "این درس شامل موارد زیر است:\n\n"
        "📚 آموزش مفهومی\n"
        "💡 نکات تخصصی\n"
        "🎯 نکات آزمونی\n"
        "🧩 مثال و کاربرد\n"
        "📝 خلاصه\n"
        "🃏 فلش‌کارت\n"
        "🧠 آزمون چهارگزینه‌ای\n"
        "📊 ثبت پیشرفت\n\n"
        "برای مطالعه، «شروع / ادامه درس» را بزن."
    )
    await callback.message.edit_text(
        text,
        reply_markup=lesson_keyboard(
            lesson_id,
            module_id,
        ),
        parse_mode="HTML",
    )
    await callback.answer()
# ============================================================
# START / CONTINUE LESSON
# ============================================================
@router.callback_query(
    F.data.startswith(START_LESSON_PREFIX)
)
async def start_lesson_handler(
    callback: CallbackQuery,
):
    if not is_allowed(
        callback.from_user.id
    ):
        await callback.answer(
            "⛔ دسترسی غیرمجاز",
            show_alert=True,
        )
        return
    try:
        lesson_id = int(
            callback.data.split(":", 1)[1]
        )
    except Exception:
        await callback.answer(
            "شناسه درس نامعتبر است.",
            show_alert=True,
        )
        return
    lesson = await get_lesson(
        lesson_id
    )
    if not lesson:
        await callback.answer(
            "درس پیدا نشد.",
            show_alert=True,
        )
        return
    module_id = lesson_module_id(
        lesson
    )
    user_id = callback.from_user.id
    try:
        await save_progress(
            user_id=user_id,
            module_id=module_id,
            lesson_id=lesson_id,
            status="started",
            completion_percent=25,
            last_position=1,
        )
    except Exception:
        logger.exception(
            "Could not save lesson progress."
        )
    text = build_lesson_text(
        lesson
    )
    text = truncate_text(
        text,
        3900,
    )
    await callback.message.edit_text(
        text,
        reply_markup=content_keyboard(
            lesson_id,
            module_id,
        ),
        parse_mode="HTML",
    )
    await callback.answer(
        "📖 درس شروع شد."
    )
# ============================================================
# BACK TO LESSON
# ============================================================
@router.callback_query(
    F.data.startswith(BACK_LESSON_PREFIX)
)
async def back_to_lesson(
    callback: CallbackQuery,
):
    if not is_allowed(
        callback.from_user.id
    ):
        await callback.answer(
            "⛔ دسترسی غیرمجاز",
            show_alert=True,
        )
        return
    try:
        lesson_id = int(
            callback.data.split(":", 1)[1]
        )
    except Exception:
        await callback.answer(
            "شناسه نامعتبر است.",
            show_alert=True,
        )
        return
    lesson = await get_lesson(
        lesson_id
    )
    if not lesson:
        await callback.answer(
            "درس پیدا نشد.",
            show_alert=True,
        )
        return
    module_id = lesson_module_id(
        lesson
    )
    title = str(
        lesson.get("title")
        or "درس"
    )
    await callback.message.edit_text(
        f"📖 <b>{title}</b>\n\n"
        "مراحل یادگیری این درس:\n\n"
        "📖 آموزش\n"
        "🃏 فلش‌کارت\n"
        "🧠 آزمون\n"
        "⭐ ذخیره",
        reply_markup=lesson_keyboard(
            lesson_id,
            module_id,
        ),
        parse_mode="HTML",
    )
    await callback.answer()
# ============================================================
# BOOKMARK
# ============================================================
@router.callback_query(
    F.data.startswith(BOOKMARK_PREFIX)
)
async def bookmark_lesson_handler(
    callback: CallbackQuery,
):
    if not is_allowed(
        callback.from_user.id
    ):
        await callback.answer(
            "⛔ دسترسی غیرمجاز",
            show_alert=True,
        )
        return
    try:
        lesson_id = int(
            callback.data.split(":", 1)[1]
        )
    except Exception:
        await callback.answer(
            "شناسه نامعتبر است.",
            show_alert=True,
        )
        return
    lesson = await get_lesson(
        lesson_id
    )
    if not lesson:
        await callback.answer(
            "درس پیدا نشد.",
            show_alert=True,
        )
        return
    try:
        await save_bookmark(
            user_id=callback.from_user.id,
            lesson_id=lesson_id,
            title=str(
                lesson.get("title")
                or "درس"
            ),
            item_type="lesson",
        )
        await callback.answer(
            "⭐ درس ذخیره شد."
        )
    except Exception:
        logger.exception(
            "Could not save lesson bookmark."
        )
        await callback.answer(
            "خطا در ذخیره درس.",
            show_alert=True,
        )
# ============================================================
# FLASHCARDS
# ============================================================
@router.callback_query(
    F.data.startswith(FLASHCARD_PREFIX)
)
async def flashcard_handler(
    callback: CallbackQuery,
):
    if not is_allowed(
        callback.from_user.id
    ):
        await callback.answer(
            "⛔ دسترسی غیرمجاز",
            show_alert=True,
        )
        return
    try:
        lesson_id = int(
            callback.data.split(":", 1)[1]
        )
    except Exception:
        await callback.answer(
            "شناسه نامعتبر است.",
            show_alert=True,
        )
        return
    lesson = await get_lesson(
        lesson_id
    )
    if not lesson:
        await callback.answer(
            "درس پیدا نشد.",
            show_alert=True,
        )
        return
    module_id = lesson_module_id(
        lesson
    )
    cards = await get_flashcards(
        user_id=callback.from_user.id,
        module_id=module_id,
        limit=20,
    )
    cards = [
        card
        for card in cards
        if card.get("lesson_id") == lesson_id
    ]
    if not cards:
        await callback.message.edit_text(
            "🃏 <b>فلش‌کارت‌های این درس</b>\n\n"
            "هنوز فلش‌کارت اختصاصی برای این درس "
            "در دیتابیس ثبت نشده است.\n\n"
            "پس از ورود محتوای آموزشی، فلش‌کارت‌ها "
            "می‌توانند به صورت خودکار ساخته شوند.",
            reply_markup=lesson_keyboard(
                lesson_id,
                module_id,
            ),
            parse_mode="HTML",
        )
        await callback.answer()
        return
    card = cards[0]
    front = str(
        card.get("front")
        or ""
    )
    back = str(
        card.get("back")
        or ""
    )
    text = (
        "🃏 <b>فلش‌کارت</b>\n\n"
        f"❓ <b>سؤال:</b>\n{front}\n\n"
        f"💡 <b>پاسخ:</b>\n{back}\n\n"
        f"📊 کارت ۱ از {len(cards)}"
    )
    await callback.message.edit_text(
        truncate_text(
            text,
            3900,
        ),
        reply_markup=lesson_keyboard(
            lesson_id,
            module_id,
        ),
        parse_mode="HTML",
    )
    await callback.answer()
# ============================================================
# QUIZ
# ============================================================
@router.callback_query(
    F.data.startswith(QUIZ_PREFIX)
)
async def quiz_start_handler(
    callback: CallbackQuery,
):
    if not is_allowed(
        callback.from_user.id
    ):
        await callback.answer(
            "⛔ دسترسی غیرمجاز",
            show_alert=True,
        )
        return
    try:
        lesson_id = int(
            callback.data.split(":", 1)[1]
        )
    except Exception:
        await callback.answer(
            "شناسه نامعتبر است.",
            show_alert=True,
        )
        return
    lesson = await get_lesson(
        lesson_id
    )
    if not lesson:
        await callback.answer(
            "درس پیدا نشد.",
            show_alert=True,
        )
        return
    questions = await get_questions(
        lesson_id=lesson_id,
        limit=10,
    )
    if not questions:
        await callback.message.edit_text(
            "🧠 <b>آزمون این درس</b>\n\n"
            "هنوز سؤالی برای این درس ثبت نشده است.\n\n"
            "بعد از ورود بانک سؤال، آزمون از همین بخش "
            "به صورت واقعی اجرا خواهد شد.",
            reply_markup=lesson_keyboard(
                lesson_id,
                lesson_module_id(lesson),
            ),
            parse_mode="HTML",
        )
        await callback.answer()
        return
    question = questions[0]
    question_id = int(
        question["id"]
    )
    options = parse_options(
        question.get("options")
    )
    if not options:
        await callback.message.edit_text(
            "⚠️ این سؤال گزینه‌های معتبری ندارد.",
            reply_markup=lesson_keyboard(
                lesson_id,
                lesson_module_id(lesson),
            ),
        )
        return
    text = (
        "🧠 <b>آزمون درس</b>\n\n"
        f"❓ <b>سؤال ۱ از {len(questions)}</b>\n\n"
        f"{question.get('question', '')}\n\n"
        "گزینه صحیح را انتخاب کن:"
    )
    await callback.message.edit_text(
        truncate_text(
            text,
            3900,
        ),
        reply_markup=quiz_question_keyboard(
            lesson_id,
            question_id,
            options,
        ),
        parse_mode="HTML",
    )
    await callback.answer()
# ============================================================
# QUIZ ANSWER
# ============================================================
@router.callback_query(
    F.data.startswith(ANSWER_PREFIX)
)
async def quiz_answer_handler(
    callback: CallbackQuery,
):
    if not is_allowed(
        callback.from_user.id
    ):
        await callback.answer(
            "⛔ دسترسی غیرمجاز",
            show_alert=True,
        )
        return
    try:
        payload = callback.data.split(
            ":",
            1,
        )[1]
        parts = payload.split(
            ":",
            2,
        )
        lesson_id = int(parts[0])
        question_id = int(parts[1])
        selected = str(parts[2])
    except Exception:
        await callback.answer(
            "پاسخ نامعتبر است.",
            show_alert=True,
        )
        return
    questions = await get_questions(
        lesson_id=lesson_id,
        limit=100,
    )
    question = None
    for item in questions:
        if int(item["id"]) == question_id:
            question = item
            break
    if question is None:
        await callback.answer(
            "سؤال پیدا نشد.",
            show_alert=True,
        )
        return
    correct_answer = (
        question.get("correct_answer")
        or question.get("answer")
    )
    selected_normalized = normalize_answer(
        selected
    )
    correct_normalized = normalize_answer(
        correct_answer
    )
    options = parse_options(
        question.get("options")
    )
    selected_display = selected
    if selected.isdigit():
        index = int(selected) - 1
        if 0 <= index < len(options):
            option = options[index]
            if isinstance(option, dict):
                selected_display = str(
                    option.get("text")
                    or option.get("label")
                    or option.get("title")
                    or option.get("value")
                    or option
                )
            else:
                selected_display = str(
                    option
                )
    is_correct = (
        selected_normalized
        == correct_normalized
    )
    if is_correct:
        result_text = "✅ <b>پاسخ صحیح است.</b>"
    else:
        result_text = "❌ <b>پاسخ اشتباه است.</b>"
    explanation = str(
        question.get("explanation")
        or ""
    ).strip()
    if not explanation:
        explanation = (
            "برای این سؤال توضیح تشریحی ثبت نشده است."
        )
    text = (
        "🧠 <b>نتیجه سؤال</b>\n\n"
        f"❓ {question.get('question', '')}\n\n"
        f"انتخاب شما: <b>{selected_display}</b>\n\n"
        f"{result_text}\n\n"
        f"💡 <b>پاسخ صحیح:</b> "
        f"{correct_answer or 'ثبت نشده'}\n\n"
        f"📝 <b>توضیح:</b>\n"
        f"{explanation}"
    )
    try:
        await update_weak_topic(
            user_id=callback.from_user.id,
            topic=(
                str(
                    question.get("source")
                    or "آزمون آموزشی"
                )
            ),
            correct=is_correct,
        )
    except Exception:
        logger.exception(
            "Could not update weak topic."
        )
    await callback.message.edit_text(
        truncate_text(
            text,
            3900,
        ),
        reply_markup=lesson_keyboard(
            lesson_id,
            None,
        ),
        parse_mode="HTML",
    )
    await callback.answer(
        "✅ پاسخ ثبت شد."
        if is_correct
        else "❌ پاسخ ثبت شد."
    )
    # Save a single-question result.
    try:
        await save_quiz_result(
            user_id=callback.from_user.id,
            total_questions=1,
            correct_answers=1 if is_correct else 0,
            wrong_answers=0 if is_correct else 1,
            score=100 if is_correct else 0,
            lesson_id=lesson_id,
            duration_seconds=0,
        )
        await save_progress(
            user_id=callback.from_user.id,
            lesson_id=lesson_id,
            status="completed"
            if is_correct
            else "started",
            completion_percent=100
            if is_correct
            else 50,
            score=100
            if is_correct
            else 0,
            last_position=2,
        )
    except Exception:
        logger.exception(
            "Could not save quiz/progress."
        )
# ============================================================
# BACK TO MODULES
# ============================================================
@router.callback_query(
    F.data == BACK_MODULES
)
async def back_modules_handler(
    callback: CallbackQuery,
):
    if not is_allowed(
        callback.from_user.id
    ):
        await callback.answer(
            "⛔ دسترسی غیرمجاز",
            show_alert=True,
        )
        return
    modules = await get_modules()
    await callback.message.edit_text(
        "📚 <b>آموزش جامع</b>\n\n"
        "ماژول آموزشی موردنظر را انتخاب کن:",
        reply_markup=modules_keyboard(
            modules
        ),
        parse_mode="HTML",
    )
    await callback.answer()
# ============================================================
# MAIN MENU CALLBACK
# ============================================================
@router.callback_query(
    F.data == "edu_main_menu"
)
async def education_main_menu_callback(
    callback: CallbackQuery,
):
    if not is_allowed(
        callback.from_user.id
    ):
        await callback.answer(
            "⛔ دسترسی غیرمجاز",
            show_alert=True,
        )
        return
    await callback.message.answer(
        "🏠 برای بازگشت کامل به منوی اصلی، "
        "دکمه «🏠 منوی اصلی» را انتخاب کن."
    )
    await callback.answer()
# ============================================================
# LEGACY TEXT LESSON SUPPORT
# ============================================================
@router.message(
    F.text.startswith("درس ")
)
async def legacy_lesson_handler(
    message: Message,
):
    if not is_allowed(
        message.from_user.id
        if message.from_user
        else None
    ):
        await deny(message)
        return
    lesson_title = message.text[4:].strip()
    if not lesson_title:
        await message.answer(
            "عنوان درس را وارد کن."
        )
        return
    modules = await get_modules()
    for module in modules:
        lessons = await get_lessons(
            int(module["id"])
        )
        for lesson in lessons:
            if str(
                lesson.get("title")
                or ""
            ).strip() == lesson_title:
                text = build_lesson_text(
                    lesson
                )
                await message.answer(
                    truncate_text(
                        text,
                        3900,
                    ),
                    reply_markup=lesson_keyboard(
                        int(lesson["id"]),
                        lesson_module_id(lesson),
                    ),
                    parse_mode="HTML",
                )
                return
    await message.answer(
        f"❌ درس «{lesson_title}» در بانک آموزشی پیدا نشد.\n\n"
        "ابتدا از «📚 آموزش جامع» ماژول و درس موردنظر را انتخاب کن."
    )
