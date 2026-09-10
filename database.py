"""
AliDaneshYarBot
database.py

SQLite database layer for:
- Users
- Educational modules
- Lessons
- Questions
- Articles
- Bookmarks
- Progress
- Quiz results
- Flashcards
- Study plans
- Settings
- Personal files
- Search history
- Weak topics
- Notifications
- Scientific sources
- Article topics

Important:
The database connection is intentionally created as an async context
manager and is NOT awaited before entering the context.

Correct usage:
    async with get_db() as db:
        ...

This avoids the aiosqlite error:
    RuntimeError: threads can only be started once
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

from config import DB_PATH

logger = logging.getLogger("AliDaneshYarBot.database")


# ============================================================
# Constants
# ============================================================

DATABASE_PATH = Path(DB_PATH)

DATABASE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Time helpers
# ============================================================

def utc_now() -> str:
    """
    Return current UTC time as ISO-8601 string.
    """
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# Database connection
# ============================================================

def get_db() -> aiosqlite.Connection:
    """
    Return a new aiosqlite connection context.

    IMPORTANT:
    Do NOT use:
        async with await get_db()

    Use:
        async with get_db() as db:
    """
    return aiosqlite.connect(
        str(DATABASE_PATH),
        timeout=30,
    )


async def configure_database(
    db: aiosqlite.Connection,
) -> None:
    """
    Configure SQLite connection.
    """

    await db.execute(
        "PRAGMA foreign_keys = ON"
    )

    await db.execute(
        "PRAGMA journal_mode = WAL"
    )

    await db.execute(
        "PRAGMA busy_timeout = 30000"
    )


# ============================================================
# Database initialization
# ============================================================

async def init_database() -> None:
    """
    Create all required database tables and indexes.
    """

    async with get_db() as db:

        await configure_database(db)

        # ----------------------------------------------------
        # Users
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'fa',
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        # ----------------------------------------------------
        # Educational modules
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_key TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                category TEXT DEFAULT 'education',
                is_active INTEGER DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        # ----------------------------------------------------
        # Lessons
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL,
                lesson_key TEXT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                content TEXT DEFAULT '',
                chapter TEXT DEFAULT '',
                lesson_order INTEGER DEFAULT 0,
                level TEXT DEFAULT '',
                keywords TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(module_id)
                    REFERENCES modules(id)
                    ON DELETE CASCADE,
                UNIQUE(module_id, lesson_key)
            )
            """
        )

        # ----------------------------------------------------
        # Questions
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER,
                lesson_id INTEGER,
                question_key TEXT,
                question TEXT NOT NULL,
                options TEXT DEFAULT '[]',
                answer TEXT,
                correct_answer TEXT,
                explanation TEXT DEFAULT '',
                difficulty TEXT DEFAULT 'medium',
                source TEXT DEFAULT '',
                year INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(module_id)
                    REFERENCES modules(id)
                    ON DELETE SET NULL,
                FOREIGN KEY(lesson_id)
                    REFERENCES lessons(id)
                    ON DELETE SET NULL
            )
            """
        )

        # ----------------------------------------------------
        # Articles
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT,
                doi TEXT,
                title TEXT NOT NULL,
                authors TEXT DEFAULT '',
                abstract TEXT DEFAULT '',
                journal TEXT DEFAULT '',
                published TEXT DEFAULT '',
                url TEXT DEFAULT '',
                pdf_url TEXT DEFAULT '',
                source TEXT DEFAULT '',
                source_id TEXT DEFAULT '',
                language TEXT DEFAULT 'en',
                topic TEXT DEFAULT '',
                keywords TEXT DEFAULT '',
                is_open_access INTEGER DEFAULT 0,
                citation_count INTEGER DEFAULT 0,
                relevance_score REAL DEFAULT 0,
                is_translated INTEGER DEFAULT 0,
                translated_title TEXT DEFAULT '',
                translated_abstract TEXT DEFAULT '',
                summary TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        # ----------------------------------------------------
        # Bookmarks
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                article_id INTEGER,
                lesson_id INTEGER,
                title TEXT DEFAULT '',
                item_type TEXT DEFAULT 'article',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(article_id)
                    REFERENCES articles(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(lesson_id)
                    REFERENCES lessons(id)
                    ON DELETE CASCADE
            )
            """
        )

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module_id INTEGER,
                lesson_id INTEGER,
                status TEXT DEFAULT 'started',
                completion_percent REAL DEFAULT 0,
                score REAL DEFAULT 0,
                study_seconds INTEGER DEFAULT 0,
                last_position INTEGER DEFAULT 0,
                last_studied_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(module_id)
                    REFERENCES modules(id)
                    ON DELETE SET NULL,
                FOREIGN KEY(lesson_id)
                    REFERENCES lessons(id)
                    ON DELETE SET NULL
            )
            """
        )

        # ----------------------------------------------------
        # Quiz results
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module_id INTEGER,
                lesson_id INTEGER,
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                wrong_answers INTEGER DEFAULT 0,
                score REAL DEFAULT 0,
                duration_seconds INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(module_id)
                    REFERENCES modules(id)
                    ON DELETE SET NULL,
                FOREIGN KEY(lesson_id)
                    REFERENCES lessons(id)
                    ON DELETE SET NULL
            )
            """
        )

        # ----------------------------------------------------
        # Flashcards
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                module_id INTEGER,
                lesson_id INTEGER,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                difficulty TEXT DEFAULT 'medium',
                review_count INTEGER DEFAULT 0,
                correct_count INTEGER DEFAULT 0,
                next_review_at TEXT,
                last_reviewed_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(module_id)
                    REFERENCES modules(id)
                    ON DELETE SET NULL,
                FOREIGN KEY(lesson_id)
                    REFERENCES lessons(id)
                    ON DELETE SET NULL
            )
            """
        )

        # ----------------------------------------------------
        # Study plans
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS study_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                plan_date TEXT,
                start_time TEXT,
                end_time TEXT,
                module_id INTEGER,
                lesson_id INTEGER,
                status TEXT DEFAULT 'planned',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(module_id)
                    REFERENCES modules(id)
                    ON DELETE SET NULL,
                FOREIGN KEY(lesson_id)
                    REFERENCES lessons(id)
                    ON DELETE SET NULL
            )
            """
        )

        # ----------------------------------------------------
        # Settings
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                key TEXT NOT NULL,
                value TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, key),
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
            """
        )

        # ----------------------------------------------------
        # Personal files
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                telegram_file_id TEXT,
                file_name TEXT NOT NULL,
                file_path TEXT DEFAULT '',
                mime_type TEXT DEFAULT '',
                file_size INTEGER DEFAULT 0,
                category TEXT DEFAULT 'other',
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
            """
        )

        # ----------------------------------------------------
        # Search history
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                search_type TEXT DEFAULT 'general',
                results_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
            """
        )

        # ----------------------------------------------------
        # Weak topics
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS weak_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                wrong_count INTEGER DEFAULT 0,
                correct_count INTEGER DEFAULT 0,
                weakness_score REAL DEFAULT 0,
                last_updated TEXT NOT NULL,
                UNIQUE(user_id, topic),
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
            """
        )

        # ----------------------------------------------------
        # Notifications
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT DEFAULT 'general',
                scheduled_at TEXT,
                sent_at TEXT,
                is_sent INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
            """
        )

        # ----------------------------------------------------
        # Scientific sources
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                source_type TEXT DEFAULT 'scientific',
                base_url TEXT DEFAULT '',
                api_url TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                last_checked_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        # ----------------------------------------------------
        # Article topics
        # ----------------------------------------------------

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS article_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                topic_key TEXT NOT NULL,
                topic_title TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                UNIQUE(article_id, topic_key),
                FOREIGN KEY(article_id)
                    REFERENCES articles(id)
                    ON DELETE CASCADE
            )
            """
        )

        # ----------------------------------------------------
        # Indexes
        # ----------------------------------------------------

        indexes = [
            """
            CREATE INDEX IF NOT EXISTS idx_users_telegram_id
            ON users(telegram_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_modules_key
            ON modules(module_key)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_lessons_module
            ON lessons(module_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_questions_module
            ON questions(module_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_questions_lesson
            ON questions(lesson_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_articles_doi
            ON articles(doi)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_articles_external_id
            ON articles(external_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_articles_source
            ON articles(source)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_articles_published
            ON articles(published)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_bookmarks_user
            ON bookmarks(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_progress_user
            ON progress(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_quiz_user
            ON quiz_results(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_flashcards_user
            ON flashcards(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_study_plans_user
            ON study_plans(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_files_user
            ON files(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_search_history_user
            ON search_history(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_weak_topics_user
            ON weak_topics(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_notifications_user
            ON notifications(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_article_topics_article
            ON article_topics(article_id)
            """,
        ]

        for statement in indexes:
            await db.execute(statement)

        await db.commit()

    logger.info(
        "SQLite database initialized at %s",
        DATABASE_PATH,
    )


# ============================================================
# Row helpers
# ============================================================

def row_to_dict(
    row: aiosqlite.Row | None,
) -> dict[str, Any] | None:

    if row is None:
        return None

    return {
        key: row[key]
        for key in row.keys()
    }


def rows_to_dicts(
    rows: list[aiosqlite.Row],
) -> list[dict[str, Any]]:

    return [
        {
            key: row[key]
            for key in row.keys()
        }
        for row in rows
    ]


# ============================================================
# Users
# ============================================================

async def register_user(
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    language: str = "fa",
) -> dict[str, Any]:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        await db.execute(
            """
            INSERT INTO users (
                telegram_id,
                username,
                first_name,
                last_name,
                language,
                is_active,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(telegram_id)
            DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                language = excluded.language,
                is_active = 1,
                updated_at = excluded.updated_at
            """,
            (
                telegram_id,
                username,
                first_name,
                last_name,
                language,
                now,
                now,
            ),
        )

        await db.commit()

        cursor = await db.execute(
            """
            SELECT *
            FROM users
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        row = await cursor.fetchone()
        await cursor.close()

        return row_to_dict(row) or {}


async def get_user(
    telegram_id: int,
) -> dict[str, Any] | None:

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT *
            FROM users
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        row = await cursor.fetchone()
        await cursor.close()

        return row_to_dict(row)


# ============================================================
# Modules
# ============================================================

async def seed_modules(
    modules: dict[str, str] | list[dict[str, Any]],
) -> None:
    """
    Insert/update educational modules.

    This function deliberately uses:
        async with get_db() as db:

    instead of:
        async with await get_db() as db

    which caused the Render crash.
    """

    if not modules:
        return

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        if isinstance(modules, dict):

            items = [
                {
                    "module_key": str(key),
                    "title": str(title),
                    "description": "",
                    "category": "education",
                    "sort_order": index,
                }
                for index, (key, title)
                in enumerate(modules.items())
            ]

        else:

            items = []

            for index, item in enumerate(modules):

                if not isinstance(item, dict):
                    continue

                module_key = (
                    item.get("module_key")
                    or item.get("key")
                    or item.get("id")
                )

                title = (
                    item.get("title")
                    or item.get("name")
                    or module_key
                )

                if not module_key or not title:
                    continue

                items.append(
                    {
                        "module_key": str(module_key),
                        "title": str(title),
                        "description": str(
                            item.get("description") or ""
                        ),
                        "category": str(
                            item.get("category")
                            or "education"
                        ),
                        "sort_order": int(
                            item.get("sort_order")
                            or index
                        ),
                    }
                )

        for item in items:

            await db.execute(
                """
                INSERT INTO modules (
                    module_key,
                    title,
                    description,
                    category,
                    is_active,
                    sort_order,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, 1, ?, ?, ?)
                ON CONFLICT(module_key)
                DO UPDATE SET
                    title = excluded.title,
                    description = excluded.description,
                    category = excluded.category,
                    sort_order = excluded.sort_order,
                    is_active = 1,
                    updated_at = excluded.updated_at
                """,
                (
                    item["module_key"],
                    item["title"],
                    item["description"],
                    item["category"],
                    item["sort_order"],
                    now,
                    now,
                ),
            )

        await db.commit()

    logger.info(
        "Educational modules seeded successfully: %s",
        len(items),
    )


async def get_modules() -> list[dict[str, Any]]:

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT *
            FROM modules
            WHERE is_active = 1
            ORDER BY sort_order ASC, id ASC
            """
        )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


async def get_module(
    module_key: str,
) -> dict[str, Any] | None:

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT *
            FROM modules
            WHERE module_key = ?
            """,
            (str(module_key).strip(),),
        )

        row = await cursor.fetchone()
        await cursor.close()

        return row_to_dict(row)


# ============================================================
# Lessons
# ============================================================

async def add_lesson(
    module_id: int,
    title: str,
    content: str = "",
    description: str = "",
    lesson_key: str | None = None,
    chapter: str = "",
    lesson_order: int = 0,
    level: str = "",
    keywords: str | list[str] = "",
) -> int:

    now = utc_now()

    if isinstance(keywords, list):
        keywords = json.dumps(
            keywords,
            ensure_ascii=False,
        )

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            INSERT INTO lessons (
                module_id,
                lesson_key,
                title,
                description,
                content,
                chapter,
                lesson_order,
                level,
                keywords,
                is_active,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                module_id,
                lesson_key,
                title,
                description,
                content,
                chapter,
                lesson_order,
                level,
                keywords,
                now,
                now,
            ),
        )

        lesson_id = cursor.lastrowid

        await db.commit()

        return int(lesson_id)


async def get_lessons(
    module_id: int,
) -> list[dict[str, Any]]:

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT *
            FROM lessons
            WHERE module_id = ?
              AND is_active = 1
            ORDER BY lesson_order ASC, id ASC
            """,
            (module_id,),
        )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


async def get_lesson(
    lesson_id: int,
) -> dict[str, Any] | None:

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT *
            FROM lessons
            WHERE id = ?
            """,
            (lesson_id,),
        )

        row = await cursor.fetchone()
        await cursor.close()

        return row_to_dict(row)


# ============================================================
# Questions
# ============================================================

async def add_question(
    question: str,
    options: list | dict | str,
    answer: str | None = None,
    correct_answer: str | None = None,
    explanation: str = "",
    module_id: int | None = None,
    lesson_id: int | None = None,
    question_key: str | None = None,
    difficulty: str = "medium",
    source: str = "",
    year: int | None = None,
) -> int:

    now = utc_now()

    if not isinstance(options, str):
        options = json.dumps(
            options,
            ensure_ascii=False,
        )

    correct = correct_answer or answer

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            INSERT INTO questions (
                module_id,
                lesson_id,
                question_key,
                question,
                options,
                answer,
                correct_answer,
                explanation,
                difficulty,
                source,
                year,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                module_id,
                lesson_id,
                question_key,
                question,
                options,
                answer,
                correct,
                explanation,
                difficulty,
                source,
                year,
                now,
                now,
            ),
        )

        question_id = cursor.lastrowid

        await db.commit()

        return int(question_id)


async def get_questions(
    module_id: int | None = None,
    lesson_id: int | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:

    limit = max(1, min(int(limit), 500))

    async with get_db() as db:

        await configure_database(db)

        if lesson_id is not None:

            cursor = await db.execute(
                """
                SELECT *
                FROM questions
                WHERE lesson_id = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (
                    lesson_id,
                    limit,
                ),
            )

        elif module_id is not None:

            cursor = await db.execute(
                """
                SELECT *
                FROM questions
                WHERE module_id = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (
                    module_id,
                    limit,
                ),
            )

        else:

            cursor = await db.execute(
                """
                SELECT *
                FROM questions
                ORDER BY id ASC
                LIMIT ?
                """,
                (limit,),
            )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


# ============================================================
# Articles
# ============================================================

async def upsert_article(
    article: dict[str, Any],
) -> int:

    now = utc_now()

    title = str(
        article.get("title")
        or "بدون عنوان"
    ).strip()

    doi = str(
        article.get("doi")
        or ""
    ).strip()

    external_id = str(
        article.get("external_id")
        or article.get("id")
        or ""
    ).strip()

    url = str(
        article.get("url")
        or article.get("source_url")
        or ""
    ).strip()

    pdf_url = str(
        article.get("pdf_url")
        or article.get("pdf")
        or ""
    ).strip()

    authors = article.get(
        "authors"
    ) or article.get("author") or ""

    if isinstance(authors, list):
        authors = json.dumps(
            authors,
            ensure_ascii=False,
        )

    abstract = str(
        article.get("abstract")
        or ""
    )

    journal = str(
        article.get("journal")
        or article.get("container_title")
        or ""
    )

    published = str(
        article.get("published")
        or article.get("published_date")
        or article.get("date")
        or ""
    )

    source = str(
        article.get("source")
        or article.get("source_name")
        or ""
    )

    source_id = str(
        article.get("source_id")
        or ""
    )

    language = str(
        article.get("language")
        or "en"
    )

    topic = str(
        article.get("topic")
        or ""
    )

    keywords = article.get(
        "keywords"
    ) or ""

    if isinstance(keywords, list):
        keywords = json.dumps(
            keywords,
            ensure_ascii=False,
        )

    is_open_access = int(
        bool(
            article.get("is_open_access")
            or article.get("open_access")
            or pdf_url
        )
    )

    citation_count = int(
        article.get("citation_count")
        or article.get("cited_by_count")
        or 0
    )

    relevance_score = float(
        article.get("relevance_score")
        or 0
    )

    translated_title = str(
        article.get("translated_title")
        or ""
    )

    translated_abstract = str(
        article.get("translated_abstract")
        or ""
    )

    summary = str(
        article.get("summary")
        or ""
    )

    is_translated = int(
        bool(
            article.get("is_translated")
            or translated_title
            or translated_abstract
        )
    )

    async with get_db() as db:

        await configure_database(db)

        existing_id = None

        if doi:

            cursor = await db.execute(
                """
                SELECT id
                FROM articles
                WHERE doi = ?
                LIMIT 1
                """,
                (doi,),
            )

            row = await cursor.fetchone()
            await cursor.close()

            if row:
                existing_id = row["id"]

        if existing_id is None and external_id:

            cursor = await db.execute(
                """
                SELECT id
                FROM articles
                WHERE external_id = ?
                LIMIT 1
                """,
                (external_id,),
            )

            row = await cursor.fetchone()
            await cursor.close()

            if row:
                existing_id = row["id"]

        if existing_id is None and url:

            cursor = await db.execute(
                """
                SELECT id
                FROM articles
                WHERE url = ?
                LIMIT 1
                """,
                (url,),
            )

            row = await cursor.fetchone()
            await cursor.close()

            if row:
                existing_id = row["id"]

        if existing_id is not None:

            await db.execute(
                """
                UPDATE articles
                SET
                    external_id = ?,
                    doi = ?,
                    title = ?,
                    authors = ?,
                    abstract = ?,
                    journal = ?,
                    published = ?,
                    url = ?,
                    pdf_url = ?,
                    source = ?,
                    source_id = ?,
                    language = ?,
                    topic = ?,
                    keywords = ?,
                    is_open_access = ?,
                    citation_count = ?,
                    relevance_score = ?,
                    is_translated = ?,
                    translated_title = ?,
                    translated_abstract = ?,
                    summary = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    external_id,
                    doi,
                    title,
                    authors,
                    abstract,
                    journal,
                    published,
                    url,
                    pdf_url,
                    source,
                    source_id,
                    language,
                    topic,
                    keywords,
                    is_open_access,
                    citation_count,
                    relevance_score,
                    is_translated,
                    translated_title,
                    translated_abstract,
                    summary,
                    now,
                    existing_id,
                ),
            )

            await db.commit()

            return int(existing_id)

        cursor = await db.execute(
            """
            INSERT INTO articles (
                external_id,
                doi,
                title,
                authors,
                abstract,
                journal,
                published,
                url,
                pdf_url,
                source,
                source_id,
                language,
                topic,
                keywords,
                is_open_access,
                citation_count,
                relevance_score,
                is_translated,
                translated_title,
                translated_abstract,
                summary,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                external_id,
                doi,
                title,
                authors,
                abstract,
                journal,
                published,
                url,
                pdf_url,
                source,
                source_id,
                language,
                topic,
                keywords,
                is_open_access,
                citation_count,
                relevance_score,
                is_translated,
                translated_title,
                translated_abstract,
                summary,
                now,
                now,
            ),
        )

        article_id = cursor.lastrowid

        await db.commit()

        return int(article_id)


async def get_article(
    article_id: int,
) -> dict[str, Any] | None:

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT *
            FROM articles
            WHERE id = ?
            """,
            (article_id,),
        )

        row = await cursor.fetchone()
        await cursor.close()

        return row_to_dict(row)


async def search_articles(
    query: str = "",
    limit: int = 10,
) -> list[dict[str, Any]]:

    limit = max(
        1,
        min(int(limit), 100),
    )

    query = str(query or "").strip()

    async with get_db() as db:

        await configure_database(db)

        if not query:

            cursor = await db.execute(
                """
                SELECT *
                FROM articles
                ORDER BY
                    published DESC,
                    relevance_score DESC,
                    id DESC
                LIMIT ?
                """,
                (limit,),
            )

        else:

            pattern = f"%{query}%"

            cursor = await db.execute(
                """
                SELECT *
                FROM articles
                WHERE
                    title LIKE ?
                    OR translated_title LIKE ?
                    OR abstract LIKE ?
                    OR translated_abstract LIKE ?
                    OR authors LIKE ?
                    OR journal LIKE ?
                    OR topic LIKE ?
                    OR keywords LIKE ?
                ORDER BY
                    relevance_score DESC,
                    published DESC,
                    id DESC
                LIMIT ?
                """,
                (
                    pattern,
                    pattern,
                    pattern,
                    pattern,
                    pattern,
                    pattern,
                    pattern,
                    pattern,
                    limit,
                ),
            )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


# ============================================================
# Bookmarks / Saved articles
# ============================================================

async def save_article(
    user_id: int,
    article_id: int,
) -> int:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT id
            FROM bookmarks
            WHERE user_id = ?
              AND article_id = ?
            LIMIT 1
            """,
            (
                user_id,
                article_id,
            ),
        )

        row = await cursor.fetchone()
        await cursor.close()

        if row:
            return int(row["id"])

        article_cursor = await db.execute(
            """
            SELECT title
            FROM articles
            WHERE id = ?
            """,
            (article_id,),
        )

        article_row = await article_cursor.fetchone()
        await article_cursor.close()

        title = (
            article_row["title"]
            if article_row
            else ""
        )

        cursor = await db.execute(
            """
            INSERT INTO bookmarks (
                user_id,
                article_id,
                title,
                item_type,
                created_at
            )
            VALUES (?, ?, ?, 'article', ?)
            """,
            (
                user_id,
                article_id,
                title,
                now,
            ),
        )

        bookmark_id = cursor.lastrowid

        await db.commit()

        return int(bookmark_id)


async def save_bookmark(
    user_id: int,
    article_id: int | None = None,
    lesson_id: int | None = None,
    title: str = "",
    item_type: str = "article",
) -> int:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            INSERT INTO bookmarks (
                user_id,
                article_id,
                lesson_id,
                title,
                item_type,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                article_id,
                lesson_id,
                title,
                item_type,
                now,
            ),
        )

        bookmark_id = cursor.lastrowid

        await db.commit()

        return int(bookmark_id)


async def delete_bookmark(
    user_id: int,
    bookmark_id: int,
) -> bool:

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            DELETE FROM bookmarks
            WHERE id = ?
              AND user_id = ?
            """,
            (
                bookmark_id,
                user_id,
            ),
        )

        deleted = cursor.rowcount > 0

        await db.commit()

        return deleted


async def get_bookmarks(
    user_id: int,
    item_type: str | None = None,
) -> list[dict[str, Any]]:

    async with get_db() as db:

        await configure_database(db)

        if item_type:

            cursor = await db.execute(
                """
                SELECT *
                FROM bookmarks
                WHERE user_id = ?
                  AND item_type = ?
                ORDER BY created_at DESC
                """,
                (
                    user_id,
                    item_type,
                ),
            )

        else:

            cursor = await db.execute(
                """
                SELECT *
                FROM bookmarks
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


# ============================================================
# Progress
# ============================================================

async def save_progress(
    user_id: int,
    module_id: int | None = None,
    lesson_id: int | None = None,
    status: str = "started",
    completion_percent: float = 0,
    score: float = 0,
    study_seconds: int = 0,
    last_position: int = 0,
) -> int:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT id
            FROM progress
            WHERE user_id = ?
              AND module_id IS ?
              AND lesson_id IS ?
            LIMIT 1
            """,
            (
                user_id,
                module_id,
                lesson_id,
            ),
        )

        row = await cursor.fetchone()
        await cursor.close()

        if row:

            progress_id = int(row["id"])

            await db.execute(
                """
                UPDATE progress
                SET
                    status = ?,
                    completion_percent = ?,
                    score = ?,
                    study_seconds = ?,
                    last_position = ?,
                    last_studied_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    status,
                    completion_percent,
                    score,
                    study_seconds,
                    last_position,
                    now,
                    now,
                    progress_id,
                ),
            )

        else:

            cursor = await db.execute(
                """
                INSERT INTO progress (
                    user_id,
                    module_id,
                    lesson_id,
                    status,
                    completion_percent,
                    score,
                    study_seconds,
                    last_position,
                    last_studied_at,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    module_id,
                    lesson_id,
                    status,
                    completion_percent,
                    score,
                    study_seconds,
                    last_position,
                    now,
                    now,
                    now,
                ),
            )

            progress_id = cursor.lastrowid

        await db.commit()

        return int(progress_id)


async def get_progress(
    user_id: int,
    module_id: int | None = None,
    lesson_id: int | None = None,
) -> list[dict[str, Any]]:

    async with get_db() as db:

        await configure_database(db)

        if lesson_id is not None:

            cursor = await db.execute(
                """
                SELECT *
                FROM progress
                WHERE user_id = ?
                  AND lesson_id = ?
                ORDER BY updated_at DESC
                """,
                (
                    user_id,
                    lesson_id,
                ),
            )

        elif module_id is not None:

            cursor = await db.execute(
                """
                SELECT *
                FROM progress
                WHERE user_id = ?
                  AND module_id = ?
                ORDER BY updated_at DESC
                """,
                (
                    user_id,
                    module_id,
                ),
            )

        else:

            cursor = await db.execute(
                """
                SELECT *
                FROM progress
                WHERE user_id = ?
                ORDER BY updated_at DESC
                """,
                (user_id,),
            )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


# ============================================================
# Quiz results
# ============================================================

async def save_quiz_result(
    user_id: int,
    total_questions: int,
    correct_answers: int,
    wrong_answers: int | None = None,
    score: float | None = None,
    module_id: int | None = None,
    lesson_id: int | None = None,
    duration_seconds: int = 0,
) -> int:

    if wrong_answers is None:
        wrong_answers = max(
            0,
            total_questions - correct_answers,
        )

    if score is None:

        if total_questions > 0:
            score = (
                correct_answers
                / total_questions
                * 100
            )
        else:
            score = 0

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            INSERT INTO quiz_results (
                user_id,
                module_id,
                lesson_id,
                total_questions,
                correct_answers,
                wrong_answers,
                score,
                duration_seconds,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                module_id,
                lesson_id,
                total_questions,
                correct_answers,
                wrong_answers,
                score,
                duration_seconds,
                now,
            ),
        )

        result_id = cursor.lastrowid

        await db.commit()

        return int(result_id)


async def get_quiz_results(
    user_id: int,
    limit: int = 50,
) -> list[dict[str, Any]]:

    limit = max(
        1,
        min(int(limit), 500),
    )

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT *
            FROM quiz_results
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                user_id,
                limit,
            ),
        )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


# ============================================================
# Flashcards
# ============================================================

async def add_flashcard(
    front: str,
    back: str,
    user_id: int | None = None,
    module_id: int | None = None,
    lesson_id: int | None = None,
    difficulty: str = "medium",
    next_review_at: str | None = None,
) -> int:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            INSERT INTO flashcards (
                user_id,
                module_id,
                lesson_id,
                front,
                back,
                difficulty,
                next_review_at,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                module_id,
                lesson_id,
                front,
                back,
                difficulty,
                next_review_at,
                now,
                now,
            ),
        )

        flashcard_id = cursor.lastrowid

        await db.commit()

        return int(flashcard_id)


async def get_flashcards(
    user_id: int | None = None,
    module_id: int | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:

    limit = max(
        1,
        min(int(limit), 500),
    )

    async with get_db() as db:

        await configure_database(db)

        conditions = []
        params: list[Any] = []

        if user_id is not None:
            conditions.append(
                "user_id = ?"
            )
            params.append(user_id)

        if module_id is not None:
            conditions.append(
                "module_id = ?"
            )
            params.append(module_id)

        where_clause = ""

        if conditions:
            where_clause = (
                "WHERE "
                + " AND ".join(conditions)
            )

        params.append(limit)

        cursor = await db.execute(
            f"""
            SELECT *
            FROM flashcards
            {where_clause}
            ORDER BY
                next_review_at IS NULL,
                next_review_at ASC,
                id ASC
            LIMIT ?
            """,
            tuple(params),
        )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


# ============================================================
# Study plans
# ============================================================

async def add_study_plan(
    user_id: int,
    title: str,
    description: str = "",
    plan_date: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    module_id: int | None = None,
    lesson_id: int | None = None,
    status: str = "planned",
) -> int:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            INSERT INTO study_plans (
                user_id,
                title,
                description,
                plan_date,
                start_time,
                end_time,
                module_id,
                lesson_id,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                title,
                description,
                plan_date,
                start_time,
                end_time,
                module_id,
                lesson_id,
                status,
                now,
                now,
            ),
        )

        plan_id = cursor.lastrowid

        await db.commit()

        return int(plan_id)


async def get_study_plans(
    user_id: int,
    plan_date: str | None = None,
) -> list[dict[str, Any]]:

    async with get_db() as db:

        await configure_database(db)

        if plan_date:

            cursor = await db.execute(
                """
                SELECT *
                FROM study_plans
                WHERE user_id = ?
                  AND plan_date = ?
                ORDER BY start_time ASC, id ASC
                """,
                (
                    user_id,
                    plan_date,
                ),
            )

        else:

            cursor = await db.execute(
                """
                SELECT *
                FROM study_plans
                WHERE user_id = ?
                ORDER BY
                    plan_date ASC,
                    start_time ASC,
                    id ASC
                """,
                (user_id,),
            )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


# ============================================================
# Settings
# ============================================================

async def set_setting(
    user_id: int | None,
    key: str,
    value: Any,
) -> None:

    now = utc_now()

    if not isinstance(value, str):
        value = json.dumps(
            value,
            ensure_ascii=False,
        )

    async with get_db() as db:

        await configure_database(db)

        await db.execute(
            """
            INSERT INTO settings (
                user_id,
                key,
                value,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, key)
            DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (
                user_id,
                key,
                value,
                now,
                now,
            ),
        )

        await db.commit()


async def get_setting(
    user_id: int | None,
    key: str,
    default: Any = None,
) -> Any:

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT value
            FROM settings
            WHERE user_id IS ?
              AND key = ?
            LIMIT 1
            """,
            (
                user_id,
                key,
            ),
        )

        row = await cursor.fetchone()
        await cursor.close()

        if not row:
            return default

        value = row["value"]

        if not isinstance(value, str):
            return value

        try:
            return json.loads(value)
        except Exception:
            return value


# ============================================================
# Files
# ============================================================

async def save_file(
    user_id: int,
    file_name: str,
    file_path: str = "",
    mime_type: str = "",
    file_size: int = 0,
    category: str = "other",
    description: str = "",
    telegram_file_id: str | None = None,
) -> int:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            INSERT INTO files (
                user_id,
                telegram_file_id,
                file_name,
                file_path,
                mime_type,
                file_size,
                category,
                description,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                telegram_file_id,
                file_name,
                file_path,
                mime_type,
                file_size,
                category,
                description,
                now,
            ),
        )

        file_id = cursor.lastrowid

        await db.commit()

        return int(file_id)


async def get_files(
    user_id: int,
    category: str | None = None,
) -> list[dict[str, Any]]:

    async with get_db() as db:

        await configure_database(db)

        if category:

            cursor = await db.execute(
                """
                SELECT *
                FROM files
                WHERE user_id = ?
                  AND category = ?
                ORDER BY created_at DESC
                """,
                (
                    user_id,
                    category,
                ),
            )

        else:

            cursor = await db.execute(
                """
                SELECT *
                FROM files
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


# ============================================================
# Search history
# ============================================================

async def save_search_history(
    user_id: int,
    query: str,
    search_type: str = "general",
    results_count: int = 0,
) -> int:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            INSERT INTO search_history (
                user_id,
                query,
                search_type,
                results_count,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                query,
                search_type,
                results_count,
                now,
            ),
        )

        history_id = cursor.lastrowid

        await db.commit()

        return int(history_id)


# ============================================================
# Weak topics
# ============================================================

async def update_weak_topic(
    user_id: int,
    topic: str,
    correct: bool,
) -> dict[str, Any] | None:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT *
            FROM weak_topics
            WHERE user_id = ?
              AND topic = ?
            LIMIT 1
            """,
            (
                user_id,
                topic,
            ),
        )

        row = await cursor.fetchone()
        await cursor.close()

        if row:

            wrong_count = int(
                row["wrong_count"]
            )

            correct_count = int(
                row["correct_count"]
            )

            if correct:
                correct_count += 1
            else:
                wrong_count += 1

            total = (
                correct_count
                + wrong_count
            )

            weakness_score = (
                wrong_count / total * 100
                if total
                else 0
            )

            await db.execute(
                """
                UPDATE weak_topics
                SET
                    wrong_count = ?,
                    correct_count = ?,
                    weakness_score = ?,
                    last_updated = ?
                WHERE id = ?
                """,
                (
                    wrong_count,
                    correct_count,
                    weakness_score,
                    now,
                    row["id"],
                ),
            )

            topic_id = row["id"]

        else:

            wrong_count = (
                0 if correct else 1
            )

            correct_count = (
                1 if correct else 0
            )

            weakness_score = (
                wrong_count * 100
                if wrong_count
                else 0
            )

            cursor = await db.execute(
                """
                INSERT INTO weak_topics (
                    user_id,
                    topic,
                    wrong_count,
                    correct_count,
                    weakness_score,
                    last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    topic,
                    wrong_count,
                    correct_count,
                    weakness_score,
                    now,
                ),
            )

            topic_id = cursor.lastrowid

        await db.commit()

        cursor = await db.execute(
            """
            SELECT *
            FROM weak_topics
            WHERE id = ?
            """,
            (topic_id,),
        )

        result = await cursor.fetchone()
        await cursor.close()

        return row_to_dict(result)


async def get_weak_topics(
    user_id: int,
    limit: int = 20,
) -> list[dict[str, Any]]:

    limit = max(
        1,
        min(int(limit), 100),
    )

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT *
            FROM weak_topics
            WHERE user_id = ?
            ORDER BY
                weakness_score DESC,
                wrong_count DESC
            LIMIT ?
            """,
            (
                user_id,
                limit,
            ),
        )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


# ============================================================
# Notifications
# ============================================================

async def add_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "general",
    scheduled_at: str | None = None,
) -> int:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            INSERT INTO notifications (
                user_id,
                title,
                message,
                notification_type,
                scheduled_at,
                is_sent,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, 0, ?)
            """,
            (
                user_id,
                title,
                message,
                notification_type,
                scheduled_at,
                now,
            ),
        )

        notification_id = cursor.lastrowid

        await db.commit()

        return int(notification_id)


async def get_pending_notifications(
    user_id: int | None = None,
) -> list[dict[str, Any]]:

    async with get_db() as db:

        await configure_database(db)

        if user_id is None:

            cursor = await db.execute(
                """
                SELECT *
                FROM notifications
                WHERE is_sent = 0
                ORDER BY
                    scheduled_at ASC,
                    id ASC
                """
            )

        else:

            cursor = await db.execute(
                """
                SELECT *
                FROM notifications
                WHERE user_id = ?
                  AND is_sent = 0
                ORDER BY
                    scheduled_at ASC,
                    id ASC
                """,
                (user_id,),
            )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


async def mark_notification_sent(
    notification_id: int,
) -> bool:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            UPDATE notifications
            SET
                is_sent = 1,
                sent_at = ?
            WHERE id = ?
            """,
            (
                now,
                notification_id,
            ),
        )

        updated = cursor.rowcount > 0

        await db.commit()

        return updated


# ============================================================
# Scientific sources
# ============================================================

async def register_source(
    name: str,
    source_type: str = "scientific",
    base_url: str = "",
    api_url: str = "",
) -> int:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        await db.execute(
            """
            INSERT INTO sources (
                name,
                source_type,
                base_url,
                api_url,
                is_active,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(name)
            DO UPDATE SET
                source_type = excluded.source_type,
                base_url = excluded.base_url,
                api_url = excluded.api_url,
                is_active = 1,
                updated_at = excluded.updated_at
            """,
            (
                name,
                source_type,
                base_url,
                api_url,
                now,
                now,
            ),
        )

        await db.commit()

        cursor = await db.execute(
            """
            SELECT id
            FROM sources
            WHERE name = ?
            """,
            (name,),
        )

        row = await cursor.fetchone()
        await cursor.close()

        return int(row["id"]) if row else 0


# ============================================================
# Article topics
# ============================================================

async def add_article_topic(
    article_id: int,
    topic_key: str,
    topic_title: str = "",
) -> int:

    now = utc_now()

    async with get_db() as db:

        await configure_database(db)

        await db.execute(
            """
            INSERT INTO article_topics (
                article_id,
                topic_key,
                topic_title,
                created_at
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(article_id, topic_key)
            DO UPDATE SET
                topic_title = excluded.topic_title
            """,
            (
                article_id,
                topic_key,
                topic_title,
                now,
            ),
        )

        await db.commit()

        cursor = await db.execute(
            """
            SELECT id
            FROM article_topics
            WHERE article_id = ?
              AND topic_key = ?
            """,
            (
                article_id,
                topic_key,
            ),
        )

        row = await cursor.fetchone()
        await cursor.close()

        return int(row["id"]) if row else 0


# ============================================================
# Statistics
# ============================================================

async def get_user_statistics(
    user_id: int,
) -> dict[str, Any]:

    async with get_db() as db:

        await configure_database(db)

        statistics: dict[str, Any] = {}

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        cursor = await db.execute(
            """
            SELECT
                COUNT(*) AS count,
                COALESCE(
                    SUM(study_seconds),
                    0
                ) AS study_seconds,
                COALESCE(
                    AVG(completion_percent),
                    0
                ) AS average_completion
            FROM progress
            WHERE user_id = ?
            """,
            (user_id,),
        )

        row = await cursor.fetchone()
        await cursor.close()

        if row:
            statistics["progress_count"] = int(
                row["count"] or 0
            )
            statistics["study_seconds"] = int(
                row["study_seconds"] or 0
            )
            statistics["average_completion"] = float(
                row["average_completion"] or 0
            )
        else:
            statistics["progress_count"] = 0
            statistics["study_seconds"] = 0
            statistics["average_completion"] = 0

        # ----------------------------------------------------
        # Quiz
        # ----------------------------------------------------

        cursor = await db.execute(
            """
            SELECT
                COUNT(*) AS quiz_count,
                COALESCE(
                    AVG(score),
                    0
                ) AS average_score,
                COALESCE(
                    SUM(correct_answers),
                    0
                ) AS correct_answers,
                COALESCE(
                    SUM(wrong_answers),
                    0
                ) AS wrong_answers
            FROM quiz_results
            WHERE user_id = ?
            """,
            (user_id,),
        )

        row = await cursor.fetchone()
        await cursor.close()

        if row:
            statistics["quiz_count"] = int(
                row["quiz_count"] or 0
            )
            statistics["average_quiz_score"] = float(
                row["average_score"] or 0
            )
            statistics["correct_answers"] = int(
                row["correct_answers"] or 0
            )
            statistics["wrong_answers"] = int(
                row["wrong_answers"] or 0
            )

        # ----------------------------------------------------
        # Bookmarks
        # ----------------------------------------------------

        cursor = await db.execute(
            """
            SELECT COUNT(*) AS count
            FROM bookmarks
            WHERE user_id = ?
            """,
            (user_id,),
        )

        row = await cursor.fetchone()
        await cursor.close()

        statistics["bookmarks"] = int(
            row["count"] or 0
        ) if row else 0

        # ----------------------------------------------------
        # Files
        # ----------------------------------------------------

        cursor = await db.execute(
            """
            SELECT COUNT(*) AS count
            FROM files
            WHERE user_id = ?
            """,
            (user_id,),
        )

        row = await cursor.fetchone()
        await cursor.close()

        statistics["files"] = int(
            row["count"] or 0
        ) if row else 0

        # ----------------------------------------------------
        # Flashcards
        # ----------------------------------------------------

        cursor = await db.execute(
            """
            SELECT COUNT(*) AS count
            FROM flashcards
            WHERE user_id = ?
            """,
            (user_id,),
        )

        row = await cursor.fetchone()
        await cursor.close()

        statistics["flashcards"] = int(
            row["count"] or 0
        ) if row else 0

        # ----------------------------------------------------
        # Study plans
        # ----------------------------------------------------

        cursor = await db.execute(
            """
            SELECT COUNT(*) AS count
            FROM study_plans
            WHERE user_id = ?
            """,
            (user_id,),
        )

        row = await cursor.fetchone()
        await cursor.close()

        statistics["study_plans"] = int(
            row["count"] or 0
        ) if row else 0

        return statistics


# ============================================================
# Compatibility helpers
# ============================================================

async def get_articles(
    limit: int = 20,
) -> list[dict[str, Any]]:

    return await search_articles(
        query="",
        limit=limit,
    )


async def delete_article(
    article_id: int,
) -> bool:

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            DELETE FROM articles
            WHERE id = ?
            """,
            (article_id,),
        )

        deleted = cursor.rowcount > 0

        await db.commit()

        return deleted


async def get_sources() -> list[dict[str, Any]]:

    async with get_db() as db:

        await configure_database(db)

        cursor = await db.execute(
            """
            SELECT *
            FROM sources
            WHERE is_active = 1
            ORDER BY name ASC
            """
        )

        rows = await cursor.fetchall()
        await cursor.close()

        return rows_to_dicts(rows)


# ============================================================
# Database health check
# ============================================================

async def database_health_check() -> dict[str, Any]:

    try:

        async with get_db() as db:

            await configure_database(db)

            cursor = await db.execute(
                """
                SELECT
                    name
                FROM sqlite_master
                WHERE type = 'table'
                ORDER BY name
                """
            )

            rows = await cursor.fetchall()
            await cursor.close()

            tables = [
                row["name"]
                for row in rows
            ]

            return {
                "status": "ok",
                "database": str(
                    DATABASE_PATH
                ),
                "tables": len(tables),
                "table_names": tables,
            }

    except Exception as exc:

        logger.exception(
            "Database health check failed."
        )

        return {
            "status": "error",
            "database": str(
                DATABASE_PATH
            ),
            "error": str(exc),
        }


# ============================================================
# Local test
# ============================================================

async def _test_database() -> None:

    await init_database()

    result = await database_health_check()

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
        _test_database()
    )
