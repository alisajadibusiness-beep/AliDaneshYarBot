from datetime import datetime, timedelta, timezone

from database import upsert_article
from services.scientific_search import search_all_sources


WATCH_TOPICS = [
    "business management",
    "banking",
    "financial management",
    "accounting",
    "marketing sales",
    "international business",
    "strategic management",
    "artificial intelligence business",
    "fintech digital banking",
]


async def collect_topic(
    topic: str,
    limit: int = 10,
) -> int:
    articles = await search_all_sources(
        query=topic,
        limit=limit,
    )

    count = 0

    for article in articles:
        article["topic"] = topic

        await upsert_article(article)
        count += 1

    return count


async def collect_latest_resources(
    limit_per_topic: int = 5,
) -> int:
    total = 0

    for topic in WATCH_TOPICS:
        try:
            total += await collect_topic(
                topic,
                limit_per_topic,
            )
        except Exception:
            continue

    return total
