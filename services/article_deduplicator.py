import re


def normalize_title(title: str) -> str:
    title = title.lower().strip()

    title = re.sub(
        r"[^a-z0-9\u0600-\u06ff\s]",
        " ",
        title,
    )

    title = re.sub(
        r"\s+",
        " ",
        title,
    )

    return title


def article_key(article: dict) -> str:
    doi = (
        article.get("doi")
        or ""
    ).strip().lower()

    if doi:
        return f"doi:{doi}"

    url = (
        article.get("url")
        or ""
    ).strip().lower()

    if url:
        return f"url:{url}"

    return (
        "title:"
        + normalize_title(
            article.get("title", "")
        )
    )


def deduplicate(
    articles: list[dict],
) -> list[dict]:
    seen = set()
    result = []

    for article in articles:
        key = article_key(article)

        if key in seen:
            continue

        seen.add(key)
        result.append(article)

    return result
