"""
AliDaneshYarBot
handlers/search.py
Smart article search handler.
Features:
- /search
- /latest
- /help_search
- Persian/Arabic text normalization
- Article database search
- Private-user access
- Search history
- Telegram-safe message splitting
"""
from __future__ import annotations
import html
import logging
import re
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ALLOWED_USER_IDS
from database import (
    save_search_history,
    search_articles,
)
logger = logging.getLogger("AliDaneshYarBot.handlers.search")
router = Router(name="search")
# ============================================================
# ACCESS CONTROL
# ============================================================
def is_allowed(
    user_id: int | None,
) -> bool:
    if user_id is None:
        return False
    return user_id in ALLOWED_USER_IDS
# ============================================================
# TEXT NORMALIZATION
# ============================================================
def normalize_text(
    text: str,
) -> str:
    if not text:
        return ""
    text = str(text).strip()
    replacements = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ة": "ه",
        "ۀ": "ه",
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
        "ٱ": "ا",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(
        r"\s+",
        " ",
        text,
    )
    return text.strip()
# ============================================================
# KNOWN SEARCH KEYWORDS
# ============================================================
SEARCH_KEYWORDS = re.compile(
    r"^(مدیریت|"
    r"بانکداری|"
    r"حسابداری|"
    r"بازاریابی|"
    r"فروش|"
    r"تجارت|"
    r"تجارت بین.?الملل|"
    r"اقتصاد|"
    r"مالی|"
    r"مدیریت مالی|"
    r"هوش مصنوعی|"
    r"هوش|"
    r"فین.?تک|"
    r"تجارت الکترونیک|"
    r"منابع انسانی|"
    r"کسب.?و.?کار|"
    r"finance|"
    r"financial|"
    r"banking|"
    r"bank|"
    r"accounting|"
    r"marketing|"
    r"sales|"
    r"management|"
    r"business|"
    r"international business|"
    r"international trade|"
    r"economics|"
    r"artificial intelligence|"
    r"fintech|"
    r"ecommerce)"
    r".*$",
    re.IGNORECASE,
)
# ============================================================
# SEARCH PREFIXES
# ============================================================
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
# ============================================================
# ARTICLE FORMATTER
# ============================================================
def format_article(
    article: dict,
    index: int,
) -> str:
    title = html.escape(
        str(
            article.get("title")
            or "بدون عنوان"
        )
    )
    authors = (
        article.get("authors")
        or article.get("author")
        or ""
    )
    if isinstance(authors, list):
        authors = ", ".join(
            str(item)
            for item in authors
        )
    authors = html.escape(
        str(authors)
    )
    published = (
        article.get("published")
        or article.get("published_date")
        or article.get("date")
        or ""
    )
    published = html.escape(
        str(published)
    )
    journal = (
        article.get("journal")
        or article.get("container_title")
        or ""
    )
    journal = html.escape(
        str(journal)
    )
    source = (
        article.get("source")
        or article.get("source_name")
        or ""
    )
    source = html.escape(
        str(source)
    )
    doi = str(
        article.get("doi")
        or ""
    ).strip()
    url = str(
        article.get("url")
        or article.get("source_url")
        or ""
    ).strip()
    pdf_url = str(
        article.get("pdf_url")
        or ""
    ).strip()
    lines = [
        f"<b>{index}. {title}</b>",
    ]
    if authors:
        lines.append(
            f"👤 نویسندگان: {authors}"
        )
    if published:
        lines.append(
            f"📅 تاریخ: {published}"
        )
    if journal:
        lines.append(
            f"📚 مجله/منبع: {journal}"
        )
    if source:
        lines.append(
            f"🔎 پایگاه: {source}"
        )
    if doi:
        lines.append(
            "🔗 DOI: "
            f"<code>{html.escape(doi)}</code>"
        )
    if url:
        safe_url = html.escape(
            url,
            quote=True,
        )
        lines.append(
            f'🌐 <a href="{safe_url}">مشاهده منبع</a>'
        )
    if pdf_url:
        safe_pdf_url = html.escape(
            pdf_url,
            quote=True,
        )
        lines.append(
            f'📄 <a href="{safe_pdf_url}">PDF قانونی</a>'
        )
    translated_title = str(
        article.get("translated_title")
        or ""
    ).strip()
    if translated_title:
        lines.append(
            "🇮🇷 عنوان فارسی: "
            + html.escape(
                translated_title
            )
        )
    summary = str(
        article.get("summary")
        or ""
    ).strip()
    if summary:
        short_summary = summary[:600]
        if len(summary) > 600:
            short_summary += "..."
        lines.append(
            "📝 خلاصه: "
            + html.escape(
                short_summary
            )
        )
    return "\n".join(lines)
# ============================================================
# DATABASE SEARCH
# ============================================================
async def perform_article_search(
    query: str = "",
    limit: int = 10,
) -> list[dict]:
    query = normalize_text(query)
    limit = max(
        1,
        min(int(limit), 50),
    )
    try:
        results = await search_articles(
            query=query,
            limit=limit,
        )
        if not results:
            return []
        return [
            dict(item)
            for item in results
        ]
    except TypeError:
        # Compatibility fallback
        try:
            results = await search_articles(
                query,
                limit,
            )
            if not results:
                return []
            return [
                dict(item)
                for item in results
            ]
        except Exception:
            logger.exception(
                "Article search failed."
            )
            return []
    except Exception:
        logger.exception(
            "Article search failed."
        )
        return []
# ============================================================
# SEARCH HISTORY
# ============================================================
async def record_search(
    user_id: int,
    query: str,
    results_count: int = 0,
) -> None:
    try:
        await save_search_history(
            user_id=user_id,
            query=query,
            search_type="articles",
            results_count=results_count,
        )
    except TypeError:
        try:
            await save_search_history(
                user_id,
                query,
                "articles",
                results_count,
            )
        except Exception:
            logger.exception(
                "Could not save search history."
            )
    except Exception:
        logger.exception(
            "Could not save search history."
        )
# ============================================================
# TELEGRAM MESSAGE SPLITTER
# ============================================================
def split_text(
    text: str,
    max_length: int = 3800,
) -> list[str]:
    if not text:
        return []
    if len(text) <= max_length:
        return [text]
    chunks: list[str] = []
    current = ""
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        candidate = (
            f"{current}\n\n{block}"
            if current
            else block
        )
        if len(candidate) <= max_length:
            current = candidate
            continue
        if current:
            chunks.append(current)
        # If one block itself is too long,
        # split it safely.
        while len(block) > max_length:
            chunks.append(
                block[:max_length]
            )
            block = block[max_length:]
        current = block
    if current:
        chunks.append(current)
    return chunks
# ============================================================
# /search
# ============================================================
@router.message(
    Command("search")
)
async def search_command(
    message: Message,
) -> None:
    user_id = (
        message.from_user.id
        if message.from_user
        else None
    )
    if not is_allowed(user_id):
        return
    args = ""
    if message.text:
        parts = message.text.split(
            maxsplit=1
        )
        if len(parts) == 2:
            args = normalize_text(
                parts[1]
            )
    if not args:
        await message.answer(
            "🔎 <b>جستجوی هوشمند</b>\n\n"
            "عبارت موردنظر را بعد از "
            "/search بنویس.\n\n"
            "مثال:\n"
            "<code>/search هوش مصنوعی در مدیریت</code>\n"
            "<code>/search banking</code>\n"
            "<code>/search international business</code>"
        )
        return
    await execute_search(
        message,
        args,
    )
# ============================================================
# KEYWORD SEARCH
# ============================================================
@router.message(
    F.text.regexp(SEARCH_KEYWORDS)
)
async def keyword_search(
    message: Message,
) -> None:
    user_id = (
        message.from_user.id
        if message.from_user
        else None
    )
    if not is_allowed(user_id):
        return
    if not message.text:
        return
    query = normalize_text(
        message.text
    )
    if len(query) < 2:
        return
    await execute_search(
        message,
        query,
    )
# ============================================================
# FALLBACK SEARCH
# ============================================================
@router.message(
    F.text
)
async def text_search_fallback(
    message: Message,
) -> None:
    user_id = (
        message.from_user.id
        if message.from_user
        else None
    )
    if not is_allowed(user_id):
        return
    if not message.text:
        return
    text = normalize_text(
        message.text
    )
    lowered = text.casefold()
    query: str | None = None
    for prefix in SEARCH_PREFIXES:
        if lowered.startswith(
            prefix.casefold()
        ):
            query = text[
                len(prefix):
            ].strip()
            break
    if not query:
        return
    if len(query) < 2:
        await message.answer(
            "🔎 عبارت جستجو خیلی کوتاه است."
        )
        return
    await execute_search(
        message,
        query,
    )
# ============================================================
# EXECUTE SEARCH
# ============================================================
async def execute_search(
    message: Message,
    query: str,
) -> None:
    query = normalize_text(
        query
    )
    if len(query) < 2:
        await message.answer(
            "🔎 لطفاً عبارت جستجوی "
            "کامل‌تری وارد کن."
        )
        return
    if len(query) > 200:
        await message.answer(
            "⚠️ عبارت جستجو بیش از حد "
            "طولانی است."
        )
        return
    searching_message = await message.answer(
        "🔎 <b>در حال جستجو...</b>\n\n"
        f"عبارت: "
        f"<code>{html.escape(query)}</code>"
    )
    user_id = (
        message.from_user.id
        if message.from_user
        else None
    )
    results = await perform_article_search(
        query=query,
        limit=10,
    )
    if user_id is not None:
        await record_search(
            user_id=user_id,
            query=query,
            results_count=len(results),
        )
    if not results:
        try:
            await searching_message.edit_text(
                "🔎 <b>نتیجه‌ای پیدا نشد.</b>\n\n"
                "عبارت جستجو:\n"
                f"<code>{html.escape(query)}</code>\n\n"
                "پیشنهاد:\n"
                "• عبارت کوتاه‌تر وارد کن\n"
                "• از کلیدواژه انگلیسی استفاده کن\n"
                "• نام موضوع یا حوزه را جستجو کن\n"
                "• ابتدا /latest را امتحان کن"
            )
        except Exception:
            await message.answer(
                "🔎 نتیجه‌ای برای جستجو پیدا نشد."
            )
        return
    output = [
        "🔎 <b>نتایج جستجو</b>",
        "",
        "عبارت: "
        f"<code>{html.escape(query)}</code>",
        f"📊 تعداد نتایج: {len(results)}",
        "",
    ]
    for index, article in enumerate(
        results,
        start=1,
    ):
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
        output.extend(
            [
                "",
                "──────────────",
                "",
            ]
        )
    text = "\n".join(output)
    chunks = split_text(
        text,
        max_length=3800,
    )
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
# ============================================================
# /latest
# ============================================================
@router.message(
    Command("latest")
)
async def latest_articles(
    message: Message,
) -> None:
    user_id = (
        message.from_user.id
        if message.from_user
        else None
    )
    if not is_allowed(user_id):
        return
    loading = await message.answer(
        "📰 <b>جدیدترین مقالات</b>\n\n"
        "در حال دریافت جدیدترین موارد..."
    )
    # IMPORTANT:
    # Empty query is intentionally allowed.
    # database.search_articles("")
    # returns latest articles.
    results = await perform_article_search(
        query="",
        limit=10,
    )
    if user_id is not None:
        await record_search(
            user_id=user_id,
            query="",
            results_count=len(results),
        )
    if not results:
        try:
            await loading.edit_text(
                "📰 <b>مقاله‌ای در پایگاه "
                "داده وجود ندارد.</b>\n\n"
                "با اجرای به‌روزرسانی علمی، "
                "مقالات جدید به پایگاه اضافه "
                "خواهند شد."
            )
        except Exception:
            await message.answer(
                "📰 مقاله‌ای در پایگاه داده وجود ندارد."
            )
        return
    output = [
        "📰 <b>جدیدترین مقالات</b>",
        "",
        f"📊 تعداد: {len(results)}",
        "",
    ]
    for index, article in enumerate(
        results,
        start=1,
    ):
        try:
            output.append(
                format_article(
                    article,
                    index,
                )
            )
        except Exception:
            logger.exception(
                "Could not format latest article."
            )
        output.extend(
            [
                "",
                "──────────────",
                "",
            ]
        )
    text = "\n".join(output)
    chunks = split_text(
        text,
        max_length=3800,
    )
    try:
        await loading.delete()
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
                "Could not send latest articles."
            )
# ============================================================
# /help_search
# ============================================================
@router.message(
    Command("help_search")
)
async def search_help(
    message: Message,
) -> None:
    user_id = (
        message.from_user.id
        if message.from_user
        else None
    )
    if not is_allowed(user_id):
        return
    await message.answer(
        "🔎 <b>راهنمای جستجوی علی دانش‌یار</b>\n\n"
        "<b>جستجوی مقاله:</b>\n"
        "<code>/search هوش مصنوعی در مدیریت</code>\n\n"
        "<b>جستجوی انگلیسی:</b>\n"
        "<code>/search banking risk</code>\n\n"
        "<b>جدیدترین مقالات:</b>\n"
        "<code>/latest</code>\n\n"
        "<b>جستجوی طبیعی:</b>\n"
        "مثلاً بنویس:\n"
        "<code>جستجوی مدیریت استراتژیک</code>\n\n"
        "<b>موضوعات:</b>\n"
        "• مدیریت\n"
        "• بانکداری\n"
        "• حسابداری\n"
        "• مدیریت مالی\n"
        "• بازاریابی\n"
        "• تجارت بین‌الملل\n"
        "• اقتصاد\n"
        "• هوش مصنوعی\n"
        "• فین‌تک\n"
        "• منابع انسانی\n"
        "• تجارت الکترونیک\n"
        "• Business\n"
        "• Management\n"
        "• Banking\n"
        "• Finance\n"
        "• Accounting\n"
        "• Marketing\n"
        "• International Business"
    )
