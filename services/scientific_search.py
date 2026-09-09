import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp


CROSSREF_URL = "https://api.crossref.org/works"
OPENALEX_URL = "https://api.openalex.org/works"


def clean_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).replace("\n", " ").strip()


async def search_crossref(
    query: str,
    limit: int = 5,
) -> list[dict]:
    params = {
        "query": query,
        "rows": limit,
        "sort": "published",
        "order": "desc",
    }

    timeout = aiohttp.ClientTimeout(total=20)

    try:
        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:
            async with session.get(
                CROSSREF_URL,
                params=params,
                headers={
                    "User-Agent":
                        "AliDaneshYarBot/1.0"
                },
            ) as response:

                if response.status != 200:
                    return []

                data = await response.json()

    except Exception:
        return []

    items = data.get("message", {}).get(
        "items", []
    )

    results = []

    for item in items:
        title_list = item.get("title") or []

        title = (
            clean_text(title_list[0])
            if title_list
            else ""
        )

        if not title:
            continue

        authors = []

        for author in item.get(
            "author", []
        ):
            name = " ".join(
                filter(
                    None,
                    [
                        author.get("given"),
                        author.get("family"),
                    ],
                )
            )

            if name:
                authors.append(name)

        published = item.get(
            "published-print"
        ) or item.get(
            "published-online"
        ) or {}

        date_parts = published.get(
            "date-parts", []
        )

        publication_date = ""

        if date_parts and date_parts[0]:
            publication_date = "-".join(
                str(x)
                for x in date_parts[0]
            )

        doi = clean_text(
            item.get("DOI", "")
        )

        url = clean_text(
            item.get("URL", "")
        )

        results.append(
            {
                "external_id": doi or url or title,
                "doi": doi,
                "title": title,
                "authors": ", ".join(authors),
                "abstract": clean_text(
                    item.get("abstract", "")
                ),
                "journal": clean_text(
                    (
                        item.get(
                            "container-title"
                        ) or [""]
                    )[0]
                ),
                "publication_date":
                    publication_date,
                "topic": query,
                "keywords": query,
                "url": url,
                "pdf_url": "",
                "source": "Crossref",
                "open_access": False,
            }
        )

    return results


async def search_openalex(
    query: str,
    limit: int = 5,
) -> list[dict]:
    params = {
        "search": query,
        "per-page": limit,
        "sort": "publication_date:desc",
    }

    timeout = aiohttp.ClientTimeout(total=20)

    try:
        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:
            async with session.get(
                OPENALEX_URL,
                params=params,
                headers={
                    "User-Agent":
                        "AliDaneshYarBot/1.0"
                },
            ) as response:

                if response.status != 200:
                    return []

                data = await response.json()

    except Exception:
        return []

    results = []

    for item in data.get("results", []):
        title = clean_text(
            item.get("display_name", "")
        )

        if not title:
            continue

        authors = []

        for author in item.get(
            "authorships", []
        ):
            author_obj = author.get(
                "author", {}
            )

            name = clean_text(
                author_obj.get(
                    "display_name", ""
                )
            )

            if name:
                authors.append(name)

        primary_location = item.get(
            "primary_location"
        ) or {}

        landing_page = clean_text(
            primary_location.get(
                "landing_page_url", ""
            )
        )

        pdf_url = clean_text(
            (
                primary_location.get(
                    "pdf"
                ) or {}
            ).get("url", "")
        )

        open_access = bool(
            (
                item.get(
                    "open_access"
                ) or {}
            ).get("is_oa", False)
        )

        results.append(
            {
                "external_id": clean_text(
                    item.get("id", "")
                ),
                "doi": clean_text(
                    item.get("doi", "")
                ),
                "title": title,
                "authors": ", ".join(authors),
                "abstract": "",
                "journal": clean_text(
                    (
                        (
                            item.get(
                                "primary_location"
                            ) or {}
                        ).get(
                            "source"
                        ) or {}
                    ).get(
                        "display_name",
                        "",
                    )
                ),
                "publication_date":
                    clean_text(
                        item.get(
                            "publication_date",
                            "",
                        )
                    ),
                "topic": query,
                "keywords": query,
                "url": landing_page,
                "pdf_url": pdf_url,
                "source": "OpenAlex",
                "open_access": open_access,
            }
        )

    return results


async def search_all_sources(
    query: str,
    limit: int = 10,
) -> list[dict]:
    each_limit = max(
        2,
        limit // 2,
    )

    crossref_task = search_crossref(
        query,
        each_limit,
    )

    openalex_task = search_openalex(
        query,
        each_limit,
    )

    crossref, openalex = await asyncio.gather(
        crossref_task,
        openalex_task,
        return_exceptions=True,
    )

    if isinstance(crossref, Exception):
        crossref = []

    if isinstance(openalex, Exception):
        openalex = []

    results = crossref + openalex

    unique = {}
    for item in results:
        key = (
            item.get("doi")
            or item.get("external_id")
            or item.get("title")
        ).lower()

        if key and key not in unique:
            unique[key] = item

    return list(unique.values())[:limit]
