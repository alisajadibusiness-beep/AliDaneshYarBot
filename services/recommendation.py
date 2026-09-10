from database import search_articles


async def recommend_articles(
    topic: str,
    limit: int = 5,
) -> list:
    return await search_articles(
        query=topic,
        limit=limit,
    )
