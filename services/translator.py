import re


def basic_persian_summary(
    title: str,
    abstract: str = "",
) -> str:
    """
    Placeholder translation/summarization layer.

    The scientific collector stores the original source.
    This function provides a clean interface for adding
    an external translation provider later.
    """

    text = (
        abstract.strip()
        if abstract
        else title.strip()
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    if len(text) > 1200:
        text = text[:1200] + "..."

    return text


async def translate_to_persian(
    text: str,
) -> str:
    """
    Translation interface.

    Currently returns the original text.
    A dedicated translation provider can be
    connected without changing the rest of
    the bot architecture.
    """

    return text.strip()
