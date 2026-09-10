import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

from config import DATA_DIR


# =========================================================
# AliDaneshYarBot - Database
# SQLite / Async
# =========================================================

DB_PATH = Path(DATA_DIR) / "bot.db"


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def get_db() -> aiosqlite.Connection:
    """
    Create and return an asynchronous SQLite connection.
    """

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    db = await aiosqlite.connect(DB_PATH)

    db.row_factory = aiosqlite.Row

    await db.execute(
        "PRAGMA foreign_keys = ON"
    )

    await db.execute(
        "PRAGMA journal_mode = WAL"
    )

    return db


def row_to_dict(
    row: aiosqlite.Row | None,
) -> dict[str, Any] | None:
    if row is None:
        return None

    return dict(row)


# ---------------------------------------------------------
# Database initialization
# ---------------------------------------------------------

async def init_database() -> None:
    """
    Create all required database tables.
    """

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            "PRAGMA foreign_keys = ON"
        )

        await db.execute(
            "PRAGMA journal_mode = WAL"
        )

        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'fa',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_users_telegram_id
            ON users(telegram_id);


            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_modules_key
            ON modules(key);


            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL,
                key TEXT,
                title TEXT NOT NULL,
                content TEXT,
                summary TEXT,
                level TEXT,
                order_index INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                FOREIGN KEY(module_id)
                    REFERENCES modules(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_lessons_module
            ON lessons(module_id);

            CREATE INDEX IF NOT EXISTS idx_lessons_key
            ON lessons(key);


            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER,
                lesson_id INTEGER,
                question TEXT NOT NULL,
                option_a TEXT,
                option_b TEXT,
                option_c TEXT,
                option_d TEXT,
                correct_answer TEXT,
                explanation TEXT,
                difficulty TEXT DEFAULT 'medium',
                source TEXT,
                exam_year INTEGER,
                exam_title TEXT,
                created_at TEXT NOT NULL,

                FOREIGN KEY(module_id)
                    REFERENCES modules(id)
                    ON DELETE SET NULL,

                FOREIGN KEY(lesson_id)
                    REFERENCES lessons(id)
                    ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_questions_module
            ON questions(module_id);

            CREATE INDEX IF NOT EXISTS idx_questions_lesson
            ON questions(lesson_id);

            CREATE INDEX IF NOT EXISTS idx_questions_exam_year
            ON questions(exam_year);


            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT,
                doi TEXT,
                title TEXT NOT NULL,
                authors TEXT,
                abstract TEXT,
                published_date TEXT,
                journal TEXT,
                topic TEXT,
                keywords TEXT,
                source TEXT,
                source_url TEXT,
                pdf_url TEXT,
                oa_status TEXT,
                language TEXT DEFAULT 'en',
                translated_title TEXT,
                translated_abstract TEXT,
                persian_summary TEXT,
                relevance_score REAL DEFAULT 0,
                citation_count INTEGER DEFAULT 0,
                is_saved INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_articles_doi
            ON articles(doi);

            CREATE INDEX IF NOT EXISTS idx_articles_external_id
            ON articles(external_id);

            CREATE INDEX IF NOT EXISTS idx_articles_topic
            ON articles(topic);

            CREATE INDEX IF NOT EXISTS idx_articles_published
            ON articles(published_date);

            CREATE INDEX IF NOT EXISTS idx_articles_source
            ON articles(source);


            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                title TEXT,
                url TEXT,
                created_at TEXT NOT NULL,

                UNIQUE(
                    telegram_id,
                    item_type,
                    item_id
                )
            );

            CREATE INDEX IF NOT EXISTS idx_bookmarks_user
            ON bookmarks(telegram_id);


            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                module_id INTEGER,
                lesson_id INTEGER,
                status TEXT DEFAULT 'started',
                score REAL DEFAULT 0,
                time_spent INTEGER DEFAULT 0,
                last_position INTEGER DEFAULT 0,
                completed_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                UNIQUE(
                    telegram_id,
                    module_id,
                    lesson_id
                )
            );

            CREATE INDEX IF NOT EXISTS idx_progress_user
            ON progress(telegram_id);


            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                quiz_type TEXT,
                module_id INTEGER,
                lesson_id INTEGER,
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                wrong_answers INTEGER DEFAULT 0,
                unanswered INTEGER DEFAULT 0,
                score REAL DEFAULT 0,
                duration_seconds INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_quiz_results_user
            ON quiz_results(telegram_id);

            CREATE INDEX IF NOT EXISTS idx_quiz_results_module
            ON quiz_results(module_id);


            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                module_id INTEGER,
                lesson_id INTEGER,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                difficulty TEXT DEFAULT 'medium',
                review_count INTEGER DEFAULT 0,
                correct_count INTEGER DEFAULT 0,
                wrong_count INTEGER DEFAULT 0,
                next_review_at TEXT,
                last_reviewed_at TEXT,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_flashcards_user
            ON flashcards(telegram_id);

            CREATE INDEX IF NOT EXISTS idx_flashcards_review
            ON flashcards(next_review_at);


            CREATE TABLE IF NOT EXISTS study_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                plan_date TEXT,
                start_time TEXT,
                duration_minutes INTEGER DEFAULT 30,
                module_id INTEGER,
                lesson_id INTEGER,
                status TEXT DEFAULT 'planned',
                reminder_enabled INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_study_plans_user
            ON study_plans(telegram_id);

            CREATE INDEX IF NOT EXISTS idx_study_plans_date
            ON study_plans(plan_date);


            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                UNIQUE(
                    telegram_id,
                    key
                )
            );

            CREATE INDEX IF NOT EXISTS idx_settings_user
            ON settings(telegram_id);


            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                file_type TEXT,
                file_name TEXT,
                telegram_file_id TEXT,
                file_path TEXT,
                mime_type TEXT,
                size_bytes INTEGER DEFAULT 0,
                description TEXT,
                extracted_text TEXT,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_files_user
            ON files(telegram_id);


            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                search_type TEXT,
                result_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_search_history_user
            ON search_history(telegram_id);


            CREATE TABLE IF NOT EXISTS weak_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                module_id INTEGER,
                topic TEXT NOT NULL,
                wrong_count INTEGER DEFAULT 0,
                total_attempts INTEGER DEFAULT 0,
                weakness_score REAL DEFAULT 0,
                updated_at TEXT NOT NULL,

                UNIQUE(
                    telegram_id,
                    module_id,
                    topic
                )
            );

            CREATE INDEX IF NOT EXISTS idx_weak_topics_user
            ON weak_topics(telegram_id);


            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT DEFAULT 'general',
                scheduled_at TEXT,
                sent_at TEXT,
                is_sent INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_notifications_user
            ON notifications(telegram_id);

            CREATE INDEX IF NOT EXISTS idx_notifications_pending
            ON notifications(is_sent, scheduled_at);


            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                source_type TEXT,
                base_url TEXT,
                api_url TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );


            CREATE TABLE IF NOT EXISTS article_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                topic_key TEXT NOT NULL,
                topic_title TEXT,
                confidence REAL DEFAULT 0,
                created_at TEXT NOT NULL,

                UNIQUE(
                    article_id,
                    topic_key
                ),

                FOREIGN KEY(article_id)
                    REFERENCES articles(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_article_topics_article
            ON article_topics(article_id);

            CREATE INDEX IF NOT EXISTS idx_article_topics_topic
            ON article_topics(topic_key);
            """
        )

        await db.commit()


# ---------------------------------------------------------
# Users
# ---------------------------------------------------------

async def register_user(
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
) -> None:

    now = utc_now()

    async with await get_db() as db:

        await db.execute(
            """
            INSERT INTO users (
                telegram_id,
                username,
                first_name,
                last_name,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)

            ON CONFLICT(telegram_id)
            DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                updated_at = excluded.updated_at
            """,
            (
                telegram_id,
                username,
                first_name,
                last_name,
                now,
                now,
            ),
        )

        await db.commit()


async def get_user(
    telegram_id: int,
) -> dict[str, Any] | None:

    async with await get_db() as db:

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


# ---------------------------------------------------------
# Modules
# ---------------------------------------------------------

async def seed_modules(
    modules: dict[str, str],
) -> None:

    now = utc_now()

    async with await get_db() as db:

        for key, title in modules.items():

            await db.execute(
                """
                INSERT INTO modules (
                    key,
                    title,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?)

                ON CONFLICT(key)
                DO UPDATE SET
                    title = excluded.title,
                    updated_at = excluded.updated_at
                """,
                (
                    key,
                    title,
                    now,
                    now,
                ),
            )

        await db.commit()


async def get_modules(
    active_only: bool = True,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        query = """
            SELECT *
            FROM modules
        """

        if active_only:
            query += """
                WHERE is_active = 1
            """

        query += """
            ORDER BY id ASC
        """

        cursor = await db.execute(query)

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


async def get_module(
    module_key: str,
) -> dict[str, Any] | None:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM modules
            WHERE key = ?
            """,
            (module_key,),
        )

        row = await cursor.fetchone()

        await cursor.close()

        return row_to_dict(row)


# ---------------------------------------------------------
# Lessons
# ---------------------------------------------------------

async def add_lesson(
    module_id: int,
    title: str,
    content: str = "",
    summary: str = "",
    level: str = "beginner",
    key: str | None = None,
    order_index: int = 0,
) -> int:

    now = utc_now()

    async with await get_db() as db:

        cursor = await db.execute(
            """
            INSERT INTO lessons (
                module_id,
                key,
                title,
                content,
                summary,
                level,
                order_index,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                module_id,
                key,
                title,
                content,
                summary,
                level,
                order_index,
                now,
                now,
            ),
        )

        await db.commit()

        return int(cursor.lastrowid)


async def get_lessons(
    module_id: int,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM lessons
            WHERE module_id = ?
              AND is_active = 1
            ORDER BY order_index ASC, id ASC
            """,
            (module_id,),
        )

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


async def get_lesson(
    lesson_id: int,
) -> dict[str, Any] | None:

    async with await get_db() as db:

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


# ---------------------------------------------------------
# Questions
# ---------------------------------------------------------

async def add_question(
    question: str,
    option_a: str = "",
    option_b: str = "",
    option_c: str = "",
    option_d: str = "",
    correct_answer: str = "",
    explanation: str = "",
    module_id: int | None = None,
    lesson_id: int | None = None,
    difficulty: str = "medium",
    source: str = "",
    exam_year: int | None = None,
    exam_title: str = "",
) -> int:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            INSERT INTO questions (
                module_id,
                lesson_id,
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                explanation,
                difficulty,
                source,
                exam_year,
                exam_title,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                module_id,
                lesson_id,
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                explanation,
                difficulty,
                source,
                exam_year,
                exam_title,
                utc_now(),
            ),
        )

        await db.commit()

        return int(cursor.lastrowid)


async def get_questions(
    module_id: int | None = None,
    lesson_id: int | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        query = """
            SELECT *
            FROM questions
            WHERE 1 = 1
        """

        params: list[Any] = []

        if module_id is not None:
            query += """
                AND module_id = ?
            """
            params.append(module_id)

        if lesson_id is not None:
            query += """
                AND lesson_id = ?
            """
            params.append(lesson_id)

        query += """
            ORDER BY RANDOM()
            LIMIT ?
        """

        params.append(limit)

        cursor = await db.execute(
            query,
            params,
        )

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


# ---------------------------------------------------------
# Articles
# ---------------------------------------------------------

async def upsert_article(
    article: dict[str, Any],
) -> int:

    now = utc_now()

    external_id = article.get(
        "external_id"
    )

    doi = article.get("doi")

    async with await get_db() as db:

        existing = None

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
            existing = await cursor.fetchone()
            await cursor.close()

        if existing is None and external_id:
            cursor = await db.execute(
                """
                SELECT id
                FROM articles
                WHERE external_id = ?
                LIMIT 1
                """,
                (external_id,),
            )
            existing = await cursor.fetchone()
            await cursor.close()

        if existing:

            article_id = int(
                existing["id"]
            )

            await db.execute(
                """
                UPDATE articles
                SET
                    title = ?,
                    authors = ?,
                    abstract = ?,
                    published_date = ?,
                    journal = ?,
                    topic = ?,
                    keywords = ?,
                    source = ?,
                    source_url = ?,
                    pdf_url = ?,
                    oa_status = ?,
                    language = ?,
                    translated_title = ?,
                    translated_abstract = ?,
                    persian_summary = ?,
                    relevance_score = ?,
                    citation_count = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    article.get("title", ""),
                    article.get("authors", ""),
                    article.get("abstract", ""),
                    article.get("published_date", ""),
                    article.get("journal", ""),
                    article.get("topic", ""),
                    article.get("keywords", ""),
                    article.get("source", ""),
                    article.get("source_url", ""),
                    article.get("pdf_url", ""),
                    article.get("oa_status", ""),
                    article.get("language", "en"),
                    article.get("translated_title", ""),
                    article.get("translated_abstract", ""),
                    article.get("persian_summary", ""),
                    float(
                        article.get(
                            "relevance_score",
                            0,
                        ) or 0
                    ),
                    int(
                        article.get(
                            "citation_count",
                            0,
                        ) or 0
                    ),
                    now,
                    article_id,
                ),
            )

        else:

            cursor = await db.execute(
                """
                INSERT INTO articles (
                    external_id,
                    doi,
                    title,
                    authors,
                    abstract,
                    published_date,
                    journal,
                    topic,
                    keywords,
                    source,
                    source_url,
                    pdf_url,
                    oa_status,
                    language,
                    translated_title,
                    translated_abstract,
                    persian_summary,
                    relevance_score,
                    citation_count,
                    is_saved,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    external_id,
                    doi,
                    article.get("title", ""),
                    article.get("authors", ""),
                    article.get("abstract", ""),
                    article.get("published_date", ""),
                    article.get("journal", ""),
                    article.get("topic", ""),
                    article.get("keywords", ""),
                    article.get("source", ""),
                    article.get("source_url", ""),
                    article.get("pdf_url", ""),
                    article.get("oa_status", ""),
                    article.get("language", "en"),
                    article.get("translated_title", ""),
                    article.get("translated_abstract", ""),
                    article.get("persian_summary", ""),
                    float(
                        article.get(
                            "relevance_score",
                            0,
                        ) or 0
                    ),
                    int(
                        article.get(
                            "citation_count",
                            0,
                        ) or 0
                    ),
                    int(
                        article.get(
                            "is_saved",
                            0,
                        ) or 0
                    ),
                    now,
                    now,
                ),
            )

            article_id = int(
                cursor.lastrowid
            )

        await db.commit()

        return article_id


async def get_article(
    article_id: int,
) -> dict[str, Any] | None:

    async with await get_db() as db:

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
    topic: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        sql = """
            SELECT *
            FROM articles
            WHERE 1 = 1
        """

        params: list[Any] = []

        if query.strip():

            like = f"%{query.strip()}%"

            sql += """
                AND (
                    title LIKE ?
                    OR translated_title LIKE ?
                    OR abstract LIKE ?
                    OR translated_abstract LIKE ?
                    OR persian_summary LIKE ?
                    OR authors LIKE ?
                    OR keywords LIKE ?
                    OR topic LIKE ?
                )
            """

            params.extend(
                [
                    like,
                    like,
                    like,
                    like,
                    like,
                    like,
                    like,
                    like,
                ]
            )

        if topic:

            sql += """
                AND topic = ?
            """

            params.append(topic)

        sql += """
            ORDER BY
                relevance_score DESC,
                published_date DESC,
                id DESC
            LIMIT ?
        """

        params.append(limit)

        cursor = await db.execute(
            sql,
            params,
        )

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


async def save_article(
    article_id: int,
) -> None:

    async with await get_db() as db:

        await db.execute(
            """
            UPDATE articles
            SET
                is_saved = 1,
                updated_at = ?
            WHERE id = ?
            """,
            (
                utc_now(),
                article_id,
            ),
        )

        await db.commit()


# ---------------------------------------------------------
# Bookmarks
# ---------------------------------------------------------

async def save_bookmark(
    telegram_id: int,
    item_type: str,
    item_id: int,
    title: str = "",
    url: str = "",
) -> None:

    async with await get_db() as db:

        await db.execute(
            """
            INSERT INTO bookmarks (
                telegram_id,
                item_type,
                item_id,
                title,
                url,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)

            ON CONFLICT(
                telegram_id,
                item_type,
                item_id
            )
            DO UPDATE SET
                title = excluded.title,
                url = excluded.url
            """,
            (
                telegram_id,
                item_type,
                item_id,
                title,
                url,
                utc_now(),
            ),
        )

        await db.commit()


async def delete_bookmark(
    telegram_id: int,
    item_type: str,
    item_id: int,
) -> None:

    async with await get_db() as db:

        await db.execute(
            """
            DELETE FROM bookmarks
            WHERE telegram_id = ?
              AND item_type = ?
              AND item_id = ?
            """,
            (
                telegram_id,
                item_type,
                item_id,
            ),
        )

        await db.commit()


async def get_bookmarks(
    telegram_id: int,
    item_type: str | None = None,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        if item_type:

            cursor = await db.execute(
                """
                SELECT *
                FROM bookmarks
                WHERE telegram_id = ?
                  AND item_type = ?
                ORDER BY id DESC
                """,
                (
                    telegram_id,
                    item_type,
                ),
            )

        else:

            cursor = await db.execute(
                """
                SELECT *
                FROM bookmarks
                WHERE telegram_id = ?
                ORDER BY id DESC
                """,
                (telegram_id,),
            )

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


# ---------------------------------------------------------
# Progress
# ---------------------------------------------------------

async def save_progress(
    telegram_id: int,
    module_id: int | None = None,
    lesson_id: int | None = None,
    status: str = "started",
    score: float = 0,
    time_spent: int = 0,
    last_position: int = 0,
    completed_at: str | None = None,
) -> None:

    now = utc_now()

    async with await get_db() as db:

        await db.execute(
            """
            INSERT INTO progress (
                telegram_id,
                module_id,
                lesson_id,
                status,
                score,
                time_spent,
                last_position,
                completed_at,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(
                telegram_id,
                module_id,
                lesson_id
            )
            DO UPDATE SET
                status = excluded.status,
                score = excluded.score,
                time_spent = excluded.time_spent,
                last_position = excluded.last_position,
                completed_at = excluded.completed_at,
                updated_at = excluded.updated_at
            """,
            (
                telegram_id,
                module_id,
                lesson_id,
                status,
                score,
                time_spent,
                last_position,
                completed_at,
                now,
                now,
            ),
        )

        await db.commit()


async def get_progress(
    telegram_id: int,
    module_id: int | None = None,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        if module_id is not None:

            cursor = await db.execute(
                """
                SELECT *
                FROM progress
                WHERE telegram_id = ?
                  AND module_id = ?
                ORDER BY updated_at DESC
                """,
                (
                    telegram_id,
                    module_id,
                ),
            )

        else:

            cursor = await db.execute(
                """
                SELECT *
                FROM progress
                WHERE telegram_id = ?
                ORDER BY updated_at DESC
                """,
                (telegram_id,),
            )

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


# ---------------------------------------------------------
# Quiz results
# ---------------------------------------------------------

async def save_quiz_result(
    telegram_id: int,
    quiz_type: str,
    total_questions: int,
    correct_answers: int,
    wrong_answers: int,
    unanswered: int = 0,
    score: float = 0,
    duration_seconds: int = 0,
    module_id: int | None = None,
    lesson_id: int | None = None,
) -> int:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            INSERT INTO quiz_results (
                telegram_id,
                quiz_type,
                module_id,
                lesson_id,
                total_questions,
                correct_answers,
                wrong_answers,
                unanswered,
                score,
                duration_seconds,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                quiz_type,
                module_id,
                lesson_id,
                total_questions,
                correct_answers,
                wrong_answers,
                unanswered,
                score,
                duration_seconds,
                utc_now(),
            ),
        )

        await db.commit()

        return int(cursor.lastrowid)


async def get_quiz_results(
    telegram_id: int,
    limit: int = 20,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM quiz_results
            WHERE telegram_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                telegram_id,
                limit,
            ),
        )

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


# ---------------------------------------------------------
# Flashcards
# ---------------------------------------------------------

async def add_flashcard(
    telegram_id: int,
    front: str,
    back: str,
    module_id: int | None = None,
    lesson_id: int | None = None,
    difficulty: str = "medium",
) -> int:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            INSERT INTO flashcards (
                telegram_id,
                module_id,
                lesson_id,
                front,
                back,
                difficulty,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                module_id,
                lesson_id,
                front,
                back,
                difficulty,
                utc_now(),
            ),
        )

        await db.commit()

        return int(cursor.lastrowid)


async def get_flashcards(
    telegram_id: int,
    limit: int = 20,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM flashcards
            WHERE telegram_id = ?
            ORDER BY
                CASE
                    WHEN next_review_at IS NULL
                    THEN 0
                    ELSE 1
                END,
                next_review_at ASC,
                id DESC
            LIMIT ?
            """,
            (
                telegram_id,
                limit,
            ),
        )

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


# ---------------------------------------------------------
# Study Plans
# ---------------------------------------------------------

async def add_study_plan(
    telegram_id: int,
    title: str,
    description: str = "",
    plan_date: str | None = None,
    start_time: str | None = None,
    duration_minutes: int = 30,
    module_id: int | None = None,
    lesson_id: int | None = None,
    reminder_enabled: bool = True,
) -> int:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            INSERT INTO study_plans (
                telegram_id,
                title,
                description,
                plan_date,
                start_time,
                duration_minutes,
                module_id,
                lesson_id,
                reminder_enabled,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                title,
                description,
                plan_date,
                start_time,
                duration_minutes,
                module_id,
                lesson_id,
                int(reminder_enabled),
                utc_now(),
                utc_now(),
            ),
        )

        await db.commit()

        return int(cursor.lastrowid)


async def get_study_plans(
    telegram_id: int,
    plan_date: str | None = None,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        if plan_date:

            cursor = await db.execute(
                """
                SELECT *
                FROM study_plans
                WHERE telegram_id = ?
                  AND plan_date = ?
                ORDER BY start_time ASC, id ASC
                """,
                (
                    telegram_id,
                    plan_date,
                ),
            )

        else:

            cursor = await db.execute(
                """
                SELECT *
                FROM study_plans
                WHERE telegram_id = ?
                ORDER BY plan_date ASC, start_time ASC
                """,
                (telegram_id,),
            )

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


# ---------------------------------------------------------
# Settings
# ---------------------------------------------------------

async def set_setting(
    telegram_id: int,
    key: str,
    value: Any,
) -> None:

    now = utc_now()

    if not isinstance(
        value,
        str,
    ):
        value = json.dumps(
            value,
            ensure_ascii=False,
        )

    async with await get_db() as db:

        await db.execute(
            """
            INSERT INTO settings (
                telegram_id,
                key,
                value,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(
                telegram_id,
                key
            )
            DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (
                telegram_id,
                key,
                value,
                now,
                now,
            ),
        )

        await db.commit()


async def get_setting(
    telegram_id: int,
    key: str,
    default: Any = None,
) -> Any:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            SELECT value
            FROM settings
            WHERE telegram_id = ?
              AND key = ?
            """,
            (
                telegram_id,
                key,
            ),
        )

        row = await cursor.fetchone()

        await cursor.close()

    if row is None:
        return default

    value = row["value"]

    try:
        return json.loads(value)
    except (
        json.JSONDecodeError,
        TypeError,
    ):
        return value


# ---------------------------------------------------------
# Search history
# ---------------------------------------------------------

async def save_search_history(
    telegram_id: int,
    query: str,
    search_type: str = "smart",
    result_count: int = 0,
) -> int:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            INSERT INTO search_history (
                telegram_id,
                query,
                search_type,
                result_count,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                query,
                search_type,
                result_count,
                utc_now(),
            ),
        )

        await db.commit()

        return int(cursor.lastrowid)


# ---------------------------------------------------------
# Files
# ---------------------------------------------------------

async def save_file(
    telegram_id: int,
    file_type: str,
    file_name: str,
    telegram_file_id: str = "",
    file_path: str = "",
    mime_type: str = "",
    size_bytes: int = 0,
    description: str = "",
    extracted_text: str = "",
) -> int:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            INSERT INTO files (
                telegram_id,
                file_type,
                file_name,
                telegram_file_id,
                file_path,
                mime_type,
                size_bytes,
                description,
                extracted_text,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                file_type,
                file_name,
                telegram_file_id,
                file_path,
                mime_type,
                size_bytes,
                description,
                extracted_text,
                utc_now(),
            ),
        )

        await db.commit()

        return int(cursor.lastrowid)


async def get_files(
    telegram_id: int,
    file_type: str | None = None,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        if file_type:

            cursor = await db.execute(
                """
                SELECT *
                FROM files
                WHERE telegram_id = ?
                  AND file_type = ?
                ORDER BY id DESC
                """,
                (
                    telegram_id,
                    file_type,
                ),
            )

        else:

            cursor = await db.execute(
                """
                SELECT *
                FROM files
                WHERE telegram_id = ?
                ORDER BY id DESC
                """,
                (telegram_id,),
            )

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


# ---------------------------------------------------------
# Weak topics
# ---------------------------------------------------------

async def update_weak_topic(
    telegram_id: int,
    topic: str,
    module_id: int | None = None,
    correct: bool = False,
) -> None:

    now = utc_now()

    async with await get_db() as db:

        cursor = await db.execute(
            """
            SELECT
                wrong_count,
                total_attempts
            FROM weak_topics
            WHERE telegram_id = ?
              AND module_id IS ?
              AND topic = ?
            """,
            (
                telegram_id,
                module_id,
                topic,
            ),
        )

        row = await cursor.fetchone()

        await cursor.close()

        if row:

            wrong_count = int(
                row["wrong_count"]
            )

            total_attempts = int(
                row["total_attempts"]
            ) + 1

            if not correct:
                wrong_count += 1

            weakness_score = (
                wrong_count / total_attempts
                if total_attempts
                else 0
            )

            await db.execute(
                """
                UPDATE weak_topics
                SET
                    wrong_count = ?,
                    total_attempts = ?,
                    weakness_score = ?,
                    updated_at = ?
                WHERE telegram_id = ?
                  AND module_id IS ?
                  AND topic = ?
                """,
                (
                    wrong_count,
                    total_attempts,
                    weakness_score,
                    now,
                    telegram_id,
                    module_id,
                    topic,
                ),
            )

        else:

            wrong_count = 0 if correct else 1
            total_attempts = 1

            await db.execute(
                """
                INSERT INTO weak_topics (
                    telegram_id,
                    module_id,
                    topic,
                    wrong_count,
                    total_attempts,
                    weakness_score,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    telegram_id,
                    module_id,
                    topic,
                    wrong_count,
                    total_attempts,
                    wrong_count / total_attempts,
                    now,
                ),
            )

        await db.commit()


async def get_weak_topics(
    telegram_id: int,
    limit: int = 10,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM weak_topics
            WHERE telegram_id = ?
            ORDER BY weakness_score DESC
            LIMIT ?
            """,
            (
                telegram_id,
                limit,
            ),
        )

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


# ---------------------------------------------------------
# Notifications
# ---------------------------------------------------------

async def add_notification(
    telegram_id: int,
    title: str,
    message: str,
    notification_type: str = "general",
    scheduled_at: str | None = None,
) -> int:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            INSERT INTO notifications (
                telegram_id,
                title,
                message,
                notification_type,
                scheduled_at,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                title,
                message,
                notification_type,
                scheduled_at,
                utc_now(),
            ),
        )

        await db.commit()

        return int(cursor.lastrowid)


async def get_pending_notifications(
    limit: int = 20,
) -> list[dict[str, Any]]:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM notifications
            WHERE is_sent = 0
              AND (
                    scheduled_at IS NULL
                    OR scheduled_at <= ?
              )
            ORDER BY
                scheduled_at ASC,
                id ASC
            LIMIT ?
            """,
            (
                utc_now(),
                limit,
            ),
        )

        rows = await cursor.fetchall()

        await cursor.close()

        return [
            dict(row)
            for row in rows
        ]


async def mark_notification_sent(
    notification_id: int,
) -> None:

    async with await get_db() as db:

        await db.execute(
            """
            UPDATE notifications
            SET
                is_sent = 1,
                sent_at = ?
            WHERE id = ?
            """,
            (
                utc_now(),
                notification_id,
            ),
        )

        await db.commit()


# ---------------------------------------------------------
# Sources
# ---------------------------------------------------------

async def register_source(
    name: str,
    source_type: str = "",
    base_url: str = "",
    api_url: str = "",
) -> int:

    now = utc_now()

    async with await get_db() as db:

        cursor = await db.execute(
            """
            INSERT INTO sources (
                name,
                source_type,
                base_url,
                api_url,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)

            ON CONFLICT(name)
            DO UPDATE SET
                source_type = excluded.source_type,
                base_url = excluded.base_url,
                api_url = excluded.api_url,
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

        return int(cursor.lastrowid or 0)


# ---------------------------------------------------------
# Statistics
# ---------------------------------------------------------

async def get_user_statistics(
    telegram_id: int,
) -> dict[str, Any]:

    async with await get_db() as db:

        cursor = await db.execute(
            """
            SELECT COUNT(*) AS count
            FROM progress
            WHERE telegram_id = ?
              AND status = 'completed'
            """,
            (telegram_id,),
        )

        completed_lessons = (
            await cursor.fetchone()
        )["count"]

        await cursor.close()


        cursor = await db.execute(
            """
            SELECT COUNT(*) AS count
            FROM quiz_results
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        quiz_count = (
            await cursor.fetchone()
        )["count"]

        await cursor.close()


        cursor = await db.execute(
            """
            SELECT
                COALESCE(
                    SUM(correct_answers),
                    0
                ) AS correct,
                COALESCE(
                    SUM(total_questions),
                    0
                ) AS total
            FROM quiz_results
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        quiz_stats = await cursor.fetchone()

        await cursor.close()


        cursor = await db.execute(
            """
            SELECT
                COUNT(*) AS count
            FROM bookmarks
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        bookmarks = (
            await cursor.fetchone()
        )["count"]

        await cursor.close()


        cursor = await db.execute(
            """
            SELECT
                COUNT(*) AS count
            FROM flashcards
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        flashcards = (
            await cursor.fetchone()
        )["count"]

        await cursor.close()


        return {
            "completed_lessons": int(
                completed_lessons or 0
            ),
            "quiz_count": int(
                quiz_count or 0
            ),
            "correct_answers": int(
                quiz_stats["correct"] or 0
            ),
            "total_questions": int(
                quiz_stats["total"] or 0
            ),
            "bookmarks": int(
                bookmarks or 0
            ),
            "flashcards": int(
                flashcards or 0
            ),
        }
