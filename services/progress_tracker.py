from database import (
    get_progress,
    save_progress,
)


async def complete_lesson(
    telegram_id: int,
    module_code: str,
    lesson_key: str,
) -> None:
    await save_progress(
        telegram_id=telegram_id,
        module_code=module_code,
        lesson_key=lesson_key,
        completed=True,
    )


async def get_user_progress(
    telegram_id: int,
) -> dict:
    rows = await get_progress(
        telegram_id
    )

    total = len(rows)

    completed = sum(
        1
        for row in rows
        if row["completed"]
    )

    percentage = (
        round(
            completed * 100 / total,
            1,
        )
        if total
        else 0
    )

    return {
        "total": total,
        "completed": completed,
        "percentage": percentage,
    }
