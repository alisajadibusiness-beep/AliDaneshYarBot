import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

_raw_ids = os.getenv("ALLOWED_USER_IDS", "").strip()
ALLOWED_USER_IDS: set[int] = set()

for value in _raw_ids.split(","):
    value = value.strip()
    if value.isdigit():
        ALLOWED_USER_IDS.add(int(value))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{DATA_DIR / 'bot.db'}",
)

AUTO_UPDATE_ENABLED = (
    os.getenv("AUTO_UPDATE_ENABLED", "true").lower()
    in {"1", "true", "yes", "on"}
)

AUTO_UPDATE_INTERVAL_HOURS = max(
    1,
    int(os.getenv("AUTO_UPDATE_INTERVAL_HOURS", "24")),
)

AUTO_UPDATE_LIMIT = max(
    1,
    int(os.getenv("AUTO_UPDATE_LIMIT", "10")),
)

APP_NAME = "AliDaneshYarBot"
BOT_NAME = "علی دانش‌یار"

TOPICS = {
    "management": "مدیریت و بازرگانی",
    "banking": "بانکداری",
    "finance": "مدیریت مالی",
    "accounting": "حسابداری",
    "marketing": "بازاریابی و فروش",
    "international_business": "تجارت بین‌الملل",
    "foundations": "دروس پایه مدیریت",
    "english": "زبان انگلیسی",
    "ai_business": "هوش مصنوعی در کسب‌وکار",
    "fintech": "فین‌تک و بانکداری دیجیتال",
}

if not ALLOWED_USER_IDS:
    print(
        "WARNING: ALLOWED_USER_IDS is empty. "
        "No Telegram user will be allowed to use the bot."
    )
