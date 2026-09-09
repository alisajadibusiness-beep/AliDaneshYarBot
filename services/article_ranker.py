from datetime import datetime, timezone


SOURCE_SCORE = {
    "OpenAlex": 1.0,
    "Crossref": 0.9,
    "arXiv": 0.85,
}


def recency_score(
    publication_date: str,
) -> float:
    if not publication_date:
        return 0.1

    try:
        date = datetime.fromisoformat(
            publication_date[:10]
        ).replace(tzinfo=timezone.utc)

        days = (
            datetime.now(timezone.utc)
            - date
        ).days

        if days <= 30:
            return 1.0

        if days <= 90:
            return 0.8

        if days <= 180:
            return 0.6

        if days <= 365:
            return 0.4

        return 0.2

    except Exception:
        return 0.1


def rank_article(
    article: dict,
) -> float:
    source = article.get(
        "source",
        "",
    )

    source_score = SOURCE_SCORE.get(
        source,
        0.5,
    )

    recent = recency_score(
        article.get(
            "publication_date",
            "",
        )
    )

    oa_score = (
        0.2
        if article.get(
            "open_access",
            False,
        )
        else 0
    )

    return round(
        recent * 0.55
        + source_score * 0.25
        + oa_score,
        4,
    )


def rank_articles(
    articles: list[dict],
) -> list[dict]:
    for article in articles:
        article["score"] = rank_article(
            article
        )

    return sorted(
        articles,
        key=lambda item: item.get(
            "score",
            0,
        ),
        reverse=True,
    )
