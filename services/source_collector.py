from services.scientific_search import (
    search_crossref,
    search_openalex,
)


async def collect_from_crossref(
    query: str,
    limit: int = 10,
) -> list[dict]:
    return await search_crossref(
        query,
        limit,
    )


async def collect_from_openalex(
    query: str,
    limit: int = 10,
) -> list[dict]:
    return await search_openalex(
        query,
        limit,
    )


async def collect_sources(
    query: str,
    limit: int = 10,
) -> list[dict]:
    results = []

    results.extend(
        await collect_from_crossref(
            query,
            limit,
        )
    )

    results.extend(
        await collect_from_openalex(
            query,
            limit,
        )
    )

    return results
