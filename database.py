import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

from config import DATA_DIR


DB_PATH = Path(DATA_DIR) / "bot.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(
            """
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_code TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT DEFAULT '',
                order_no INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_code TEXT NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                answer INTEGER NOT NULL,
                explanation TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT,
                doi TEXT,
                title TEXT NOT NULL,
                authors TEXT DEFAULT '',
                abstract TEXT DEFAULT '',
                journal TEXT DEFAULT '',
                publication_date TEXT DEFAULT '',
                topic TEXT DEFAULT '',
                keywords TEXT DEFAULT '',
                url TEXT DEFAULT '',
                pdf_url TEXT DEFAULT '',
                source TEXT DEFAULT '',
                open_access INTEGER DEFAULT 0,
                score REAL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(external_id, source)
            );

            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                article_id INTEGER,
                item_type TEXT NOT NULL,
                item_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(telegram_id, item_type, item_key)
            );

            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                module_code TEXT NOT NULL,
                lesson_key TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                score REAL DEFAULT 0,
                updated_at TEXT NOT NULL,
                UNIQUE(telegram_id, module_code, lesson_key)
            );

            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                module_code TEXT NOT NULL,
                total INTEGER NOT NULL,
                correct INTEGER NOT NULL,
                percentage REAL NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                module_code TEXT NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS study_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                target_date TEXT DEFAULT '',
                completed INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                telegram_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT DEFAULT '',
                updated_at TEXT NOT NULL,
                PRIMARY KEY(telegram_id, key)
            );
            """
        )

        await db.commit()


async def register_user(
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
) -> None:
    now = utc_now()

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users
            (telegram_id, username, first_name, last_name, created_at, last_seen_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                last_name=excluded.last_name,
                last_seen_at=excluded.last_seen_at
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


async def seed_modules(modules: dict[str, str]) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        for code, title in modules.items():
            await db.execute(
                """
                INSERT INTO modules
                (code, title, description, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(code) DO NOTHING
                """,
                (
                    code,
                    title,
                    "",
                    utc_now(),
                ),
            )

        await db.commit()


async def get_modules() -> list[aiosqlite.Row]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM modules
            ORDER BY id
            """
        )

        return await cursor.fetchall()


async def upsert_article(article: dict[str, Any]) -> int | None:
    async with aiosqlite.connect(DB_PATH) as db:
        now = utc_now()

        external_id = article.get("external_id", "")
        source = article.get("source", "")

        cursor = await db.execute(
            """
            SELECT id
            FROM articles
            WHERE external_id = ?
              AND source = ?
            LIMIT 1
            """,
            (external_id, source),
        )

        existing = await cursor.fetchone()

        if existing:
            await db.execute(
                """
                UPDATE articles
                SET doi=?,
                    title=?,
                    authors=?,
                    abstract=?,
                    journal=?,
                    publication_date=?,
                    topic=?,
                    keywords=?,
                    url=?,
                    pdf_url=?,
                    open_access=?,
                    score=?,
                    updated_at=?
                WHERE id=?
                """,
                (
                    article.get("doi", ""),
                    article.get("title", ""),
                    article.get("authors", ""),
                    article.get("abstract", ""),
                    article.get("journal", ""),
                    article.get("publication_date", ""),
                    article.get("topic", ""),
                    article.get("keywords", ""),
                    article.get("url", ""),
                    article.get("pdf_url", ""),
                    int(article.get("open_access", False)),
                    float(article.get("score", 0)),
                    now,
                    existing[0],
                ),
            )

            await db.commit()
            return existing[0]

        cursor = await db.execute(
            """
            INSERT INTO articles
            (
                external_id,
                doi,
                title,
                authors,
                abstract,
                journal,
                publication_date,
                topic,
                keywords,
                url,
                pdf_url,
                source,
                open_access,
                score,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                external_id,
                article.get("doi", ""),
                article.get("title", ""),
                article.get("authors", ""),
                article.get("abstract", ""),
                article.get("journal", ""),
                article.get("publication_date", ""),
                article.get("topic", ""),
                article.get("keywords", ""),
                article.get("url", ""),
                article.get("pdf_url", ""),
                source,
                int(article.get("open_access", False)),
                float(article.get("score", 0)),
                now,
                now,
            ),
        )

        article_id = cursor.lastrowid
        await db.commit()

        return article_id


async def search_articles(
    query: str,
    limit: int = 10,
) -> list[aiosqlite.Row]:
    query_like = f"%{query}%"

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM articles
            WHERE title LIKE ?
               OR abstract LIKE ?
               OR keywords LIKE ?
               OR topic LIKE ?
            ORDER BY score DESC, publication_date DESC
            LIMIT ?
            """,
            (
                query_like,
                query_like,
                query_like,
                query_like,
                limit,
            ),
        )

        return await cursor.fetchall()


async def get_article(article_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM articles
            WHERE id=?
            """,
            (article_id,),
        )

        return await cursor.fetchone()


async def save_bookmark(
    telegram_id: int,
    item_type: str,
    item_key: str,
    article_id: int | None = None,
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO bookmarks
            (telegram_id, article_id, item_type, item_key, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                article_id,
                item_type,
                item_key,
                utc_now(),
            ),
        )
        await db.commit()


async def get_bookmarks(
    telegram_id: int,
    limit: int = 50,
) -> list[aiosqlite.Row]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT b.*, a.title, a.url
            FROM bookmarks b
            LEFT JOIN articles a
                ON a.id = b.article_id
            WHERE b.telegram_id=?
            ORDER BY b.created_at DESC
            LIMIT ?
            """,
            (telegram_id, limit),
        )

        return await cursor.fetchall()


async def save_progress(
    telegram_id: int,
    module_code: str,
    lesson_key: str,
    completed: bool = True,
    score: float = 0,
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO progress
            (
                telegram_id,
                module_code,
                lesson_key,
                completed,
                score,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id, module_code, lesson_key)
            DO UPDATE SET
                completed=excluded.completed,
                score=excluded.score,
                updated_at=excluded.updated_at
            """,
            (
                telegram_id,
                module_code,
                lesson_key,
                int(completed),
                score,
                utc_now(),
            ),
        )
        await db.commit()


async def get_progress(
    telegram_id: int,
) -> list[aiosqlite.Row]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM progress
            WHERE telegram_id=?
            ORDER BY updated_at DESC
            """,
            (telegram_id,),
        )

        return await cursor.fetchall()


async def save_quiz_result(
    telegram_id: int,
    module_code: str,
    total: int,
    correct: int,
) -> None:
    percentage = (
        round(correct * 100 / total, 2)
        if total
        else 0
    )

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO quiz_results
            (
                telegram_id,
                module_code,
                total,
                correct,
                percentage,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                module_code,
                total,
                correct,
                percentage,
                utc_now(),
            ),
        )
        await db.commit()


async def set_setting(
    telegram_id: int,
    key: str,
    value: Any,
) -> None:
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO settings
            (telegram_id, key, value, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_id, key)
            DO UPDATE SET
                value=excluded.value,
                updated_at=excluded.updated_at
            """,
            (
                telegram_id,
                key,
                value,
                utc_now(),
            ),
        )
        await db.commit()


async def get_setting(
    telegram_id: int,
    key: str,
    default: str = "",
) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT value
            FROM settings
            WHERE telegram_id=?
              AND key=?
            """,
            (telegram_id, key),
        )

        row = await cursor.fetchone()

        return row[0] if row else default
