"""
handlers/search.py
جستجوی هوشمند ربات علی دانش‌یار
"""

import re
import html
import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from config import ALLOWED_USER_IDS
from database import search_articles, save_search_history

logger = logging.getLogger(__name__)

router = Router(name="search")


# ---------------------------------------------------------
# دسترسی خصوصی
# ---------------------------------------------------------

def is_allowed(user_id: int | None) -> bool:
    if user_id is None:
        return False
    return user_id in ALLOWED_USER_IDS


# ---------------------------------------------------------
# نرمال‌سازی متن
# ---------------------------------------------------------

def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    # یکسان‌سازی حروف فارسی/عربی
    text = text.replace("ي", "ی")
    text = text.replace("ى", "ی")
    text = text.replace("ك", "ک")
    text = text.replace("ة", "ه")
    text = text.replace("ۀ", "ه")
    text = text.replace("ؤ", "و")
    text = text.replace("إ", "ا")
    text = text.replace("أ", "ا")
    text = text.replace("ٱ", "ا")

    # فاصله‌های اضافی
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------------
# کلیدواژه‌های شناخته‌شده
# ---------------------------------------------------------

SEARCH_KEYWORDS = re.compile(
    r"^(مدیریت|بانکداری|حسابداری|بازاریابی|فروش|تجارت|"
    r"تجارت بین.?الملل|اقتصاد|مالی|مدیریت مالی|"
    r"هوش مصنوعی|هوش|فین.?تک|تجارت الکترونیک|"
    r"منابع انسانی|کسب.?و.?کار|"
    r"finance|financial|banking|bank|accounting|"
    r"marketing|sales|management|business|"
    r"international business|international trade|"
    r"economics|artificial intelligence|"
    r"fintech|ecommerce)"
    r".*",
    re.IGNORECASE,
)


# ---------------------------------------------------------
# نمایش نتایج
# ---------------------------------------------------------

def format_article(article: dict, index: int) -> str:
    title = html.escape(
        str(article.get("title") or "بدون عنوان")
    )

    authors = article.get("authors") or article.get("author") or ""
    authors = html.escape(str(authors))

    published = (
        article.get("published")
        or article.get("published_date")
        or article.get("date")
        or ""
    )
    published = html.escape(str(published))

    journal = article.get("journal") or article.get("container_title") or ""
    journal = html.escape(str(journal))

    source = article.get("source") or article.get("source_name") or ""
    source = html.escape(str(source))

    doi = article.get("doi") or ""
    url = article.get("url") or article.get("source_url") or ""

    lines = [
        f"<b>{index}. {title}</b>",
    ]

    if authors:
        lines.append(f"👤 نویسندگان: {authors}")

    if published:
        lines.append(f"📅 تاریخ: {published}")

    if journal:
        lines.append(f"📚 مجله/منبع: {journal}")

    if source:
        lines.append(f"🔎 منبع: {source}")

    if doi:
        lines.append(
            f"🔗 DOI: <code>{html.escape(str(doi))}</code>"
        )

    if url:
        safe_url = html.escape(str(url), quote=True)
        lines.append(f'🌐 <a href="{safe_url}">مشاهده منبع</a>')

    return "\n".join(lines)


# ---------------------------------------------------------
# جستجوی مقاله
# ---------------------------------------------------------

async def perform_article_search(
    query: str,
    limit: int = 10,
) -> list[dict]:

    query = normalize_text(query)

    if not query:
        return []

    try:
        results = await search_articles(
            query=query,
            limit=limit,
        )

        if results is None:
            return []

        return [
            dict(item)
            for item in results
        ]

    except TypeError:
        # سازگاری با نسخه‌هایی که search_articles
        # پارامترهای متفاوت دارند
        try:
            results = await search_articles(query, limit)
            if results is None:
                return []

            return [
                dict(item)
                for item in results
            ]

        except Exception:
            logger.exception(
                "Article search failed for query: %s",
                query,
            )
            return []

    except Exception:
        logger.exception(
            "Article search failed for query: %s",
            query,
        )
        return []


# ---------------------------------------------------------
# ثبت تاریخچه جستجو
# ---------------------------------------------------------

async def record_search(
    user_id: int,
    query: str,
) -> None:

    try:
        await save_search_history(
            user_id=user_id,
            query=query,
            search_type="articles",
        )

    except TypeError:
        # سازگاری با نسخه‌های قدیمی‌تر database.py
        try:
            await save_search_history(
                user_id,
                query,
                "articles",
            )
        except Exception:
            logger.exception(
                "Could not save search history."
            )

    except Exception:
        logger.exception(
            "Could not save search history."
        )


# ---------------------------------------------------------
# دستور /search
# ---------------------------------------------------------

@router.message(Command("search"))
async def search_command(message: Message) -> None:

    if not is_allowed(message.from_user.id if message.from_user else None):
        return

    args = ""

    if message.text:
        parts = message.text.split(maxsplit=1)

        if len(parts) == 2:
            args = normalize_text(parts[1])

    if not args:
        await message.answer(
            "🔎 <b>جستجوی هوشمند</b>\n\n"
            "عبارت موردنظر را بعد از دستور /search بنویس.\n\n"
            "مثال:\n"
            "<code>/search هوش مصنوعی در مدیریت</code>\n"
            "<code>/search banking</code>\n"
            "<code>/search international business</code>",
        )
        return

    await execute_search(message, args)


# ---------------------------------------------------------
# جستجوی عمومی متنی
# ---------------------------------------------------------

@router.message(
    F.text.regexp(
        SEARCH_KEYWORDS
    )
)
async def keyword_search(message: Message) -> None:

    if not is_allowed(message.from_user.id if message.from_user else None):
        return

    if not message.text:
        return

    query = normalize_text(message.text)

    if len(query) < 2:
        return

    await execute_search(message, query)


# ---------------------------------------------------------
# تشخیص درخواست جستجو
# ---------------------------------------------------------

SEARCH_PREFIXES = (
    "جستجو ",
    "جستجوی ",
    "جست‌وجو ",
    "جست‌وجوی ",
    "search ",
    "find ",
    "مقاله ",
    "مقالات ",
)


@router.message(F.text)
async def text_search_fallback(message: Message) -> None:

    if not is_allowed(message.from_user.id if message.from_user else None):
        return

    if not message.text:
        return

    text = normalize_text(message.text)

    lowered = text.lower()

    query = None

    for prefix in SEARCH_PREFIXES:
        if lowered.startswith(prefix.lower()):
            query = text[len(prefix):].strip()
            break

    if not query:
        return

    if len(query) < 2:
        await message.answer(
            "🔎 عبارت جستجو خیلی کوتاه است."
        )
        return

    await execute_search(message, query)


# ---------------------------------------------------------
# اجرای جستجو
# ---------------------------------------------------------

async def execute_search(
    message: Message,
    query: str,
) -> None:

    query = normalize_text(query)

    if len(query) < 2:
        await message.answer(
            "🔎 لطفاً عبارت جستجوی کامل‌تری وارد کن."
        )
        return

    if len(query) > 200:
        await message.answer(
            "⚠️ عبارت جستجو بیش از حد طولانی است."
        )
        return

    searching_message = await message.answer(
        "🔎 <b>در حال جستجو...</b>\n\n"
        f"عبارت: <code>{html.escape(query)}</code>"
    )

    user_id = (
        message.from_user.id
        if message.from_user
        else None
    )

    if user_id is not None:
        await record_search(
            user_id=user_id,
            query=query,
        )

    results = await perform_article_search(
        query=query,
        limit=10,
    )

    if not results:
        try:
            await searching_message.edit_text(
                "🔎 <b>نتیجه‌ای پیدا نشد.</b>\n\n"
                f"عبارت جستجو:\n"
                f"<code>{html.escape(query)}</code>\n\n"
                "پیشنهاد:\n"
                "• عبارت کوتاه‌تر وارد کن\n"
                "• از کلیدواژه انگلیسی استفاده کن\n"
                "• نام موضوع یا حوزه را جستجو کن"
            )
        except Exception:
            await message.answer(
                "🔎 نتیجه‌ای برای جستجو پیدا نشد."
            )

        return

    output = [
        "🔎 <b>نتایج جستجو</b>",
        "",
        f"عبارت: <code>{html.escape(query)}</code>",
        f"📊 تعداد نتایج: {len(results)}",
        "",
    ]

    for index, article in enumerate(results, start=1):

        try:
            output.append(
                format_article(
                    article,
                    index,
                )
            )
        except Exception:
            logger.exception(
                "Could not format article."
            )

        output.append("")
        output.append("──────────────")
        output.append("")

    text = "\n".join(output)

    # تلگرام محدودیت طول پیام دارد.
    # نتایج را در صورت نیاز به چند پیام تقسیم می‌کنیم.
    MAX_LENGTH = 3800

    chunks = []

    if len(text) <= MAX_LENGTH:
        chunks = [text]
    else:
        current = ""

        for block in output:
            if len(current) + len(block) + 1 > MAX_LENGTH:
                if current:
                    chunks.append(current)
                current = block
            else:
                if current:
                    current += "\n" + block
                else:
                    current = block

        if current:
            chunks.append(current)

    try:
        await searching_message.delete()
    except Exception:
        pass

    for chunk in chunks:
        try:
            await message.answer(
                chunk,
                disable_web_page_preview=True,
            )
        except Exception:
            logger.exception(
                "Could not send search result."
            )


# ---------------------------------------------------------
# /latest
# ---------------------------------------------------------

@router.message(Command("latest"))
async def latest_articles(message: Message) -> None:

    if not is_allowed(message.from_user.id if message.from_user else None):
        return

    await message.answer(
        "📰 <b>جدیدترین مقالات</b>\n\n"
        "در حال دریافت جدیدترین موارد..."
    )

    results = await perform_article_search(
        query="",
        limit=10,
    )

    if not results:
        await message.answer(
            "📰 در حال حاضر مقاله‌ای در پایگاه داده وجود ندارد."
        )
        return

    output = [
        "📰 <b>جدیدترین مقالات</b>",
        "",
    ]

    for index, article in enumerate(results, start=1):
        output.append(
            format_article(
                article,
                index,
            )
        )
        output.append("")
        output.append("──────────────")
        output.append("")

    text = "\n".join(output)

    for start in range(0, len(text), 3800):
        await message.answer(
            text[start:start + 3800],
            disable_web_page_preview=True,
        )


# ---------------------------------------------------------
# /help_search
# ---------------------------------------------------------

@router.message(Command("help_search"))
async def search_help(message: Message) -> None:

    if not is_allowed(message.from_user.id if message.from_user else None):
        return

    await message.answer(
        "🔎 <b>راهنمای جستجوی علی دانش‌یار</b>\n\n"
        "<b>جستجوی مقاله:</b>\n"
        "<code>/search هوش مصنوعی در مدیریت</code>\n\n"
        "<b>جستجوی انگلیسی:</b>\n"
        "<code>/search banking risk</code>\n\n"
        "<b>موضوعات قابل جستجو:</b>\n"
        "• مدیریت\n"
        "• بانکداری\n"
        "• حسابداری\n"
        "• مدیریت مالی\n"
        "• بازاریابی و فروش\n"
        "• تجارت بین‌الملل\n"
        "• اقتصاد\n"
        "• منابع انسانی\n"
        "• هوش مصنوعی\n"
        "• فین‌تک\n"
        "• تجارت الکترونیک\n\n"
        "<b>نمونه:</b>\n"
        "<code>/search artificial intelligence business</code>"
    )
