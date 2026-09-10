import os
from pathlib import Path

from dotenv import load_dotenv


# =========================================================
# AliDaneshYarBot - Configuration
# =========================================================

load_dotenv()


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PDF_DIR = DATA_DIR / "pdfs"
PDF_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

FILES_DIR = DATA_DIR / "files"
FILES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Telegram Bot
# ---------------------------------------------------------

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    "",
).strip()


# ---------------------------------------------------------
# Private access
# ---------------------------------------------------------

def load_allowed_user_ids() -> set[int]:
    """
    Read Telegram user IDs from:

        ALLOWED_USER_IDS=123456789,987654321

    Only numeric IDs are accepted.
    """

    raw = os.getenv(
        "ALLOWED_USER_IDS",
        "",
    ).strip()

    user_ids: set[int] = set()

    if not raw:
        return user_ids

    for value in raw.split(","):
        value = value.strip()

        if not value:
            continue

        try:
            user_ids.add(int(value))
        except ValueError:
            continue

    return user_ids


ALLOWED_USER_IDS = load_allowed_user_ids()


# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{DATA_DIR / 'bot.db'}",
).strip()


DB_PATH = DATA_DIR / "bot.db"


# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

APP_NAME = "AliDaneshYarBot"

BOT_NAME = "علی دانش‌یار"

BOT_DESCRIPTION = (
    "دستیار شخصی پژوهش، آموزش و آمادگی آزمون"
)


# ---------------------------------------------------------
# Automatic scientific resource collector
# ---------------------------------------------------------

AUTO_UPDATE_ENABLED = (
    os.getenv(
        "AUTO_UPDATE_ENABLED",
        "true",
    ).strip().lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)


try:
    AUTO_UPDATE_INTERVAL_HOURS = int(
        os.getenv(
            "AUTO_UPDATE_INTERVAL_HOURS",
            "24",
        )
    )
except ValueError:
    AUTO_UPDATE_INTERVAL_HOURS = 24


AUTO_UPDATE_INTERVAL_HOURS = max(
    1,
    AUTO_UPDATE_INTERVAL_HOURS,
)


try:
    AUTO_UPDATE_LIMIT = int(
        os.getenv(
            "AUTO_UPDATE_LIMIT",
            "5",
        )
    )
except ValueError:
    AUTO_UPDATE_LIMIT = 5


AUTO_UPDATE_LIMIT = max(
    1,
    AUTO_UPDATE_LIMIT,
)


# ---------------------------------------------------------
# Scientific search
# ---------------------------------------------------------

CROSSREF_API_URL = (
    "https://api.crossref.org/works"
)

OPENALEX_API_URL = (
    "https://api.openalex.org/works"
)

ARXIV_API_URL = (
    "https://export.arxiv.org/api/query"
)


SCIENTIFIC_SOURCES = [
    "Crossref",
    "OpenAlex",
    "arXiv",
]


# ---------------------------------------------------------
# Topics monitored automatically
# ---------------------------------------------------------

WATCH_TOPICS = {
    "management": {
        "title": "مدیریت و بازرگانی",
        "queries": [
            "business management",
            "management",
            "strategic management",
            "organizational behavior",
        ],
    },

    "banking": {
        "title": "بانکداری",
        "queries": [
            "banking",
            "bank management",
            "banking risk",
            "digital banking",
        ],
    },

    "finance": {
        "title": "مدیریت مالی",
        "queries": [
            "financial management",
            "corporate finance",
            "financial decision making",
            "investment management",
        ],
    },

    "accounting": {
        "title": "حسابداری",
        "queries": [
            "accounting",
            "financial accounting",
            "management accounting",
            "accounting information systems",
        ],
    },

    "marketing": {
        "title": "بازاریابی و فروش",
        "queries": [
            "marketing",
            "digital marketing",
            "sales management",
            "consumer behavior",
        ],
    },

    "international_business": {
        "title": "تجارت بین‌الملل",
        "queries": [
            "international business",
            "international trade",
            "global business",
            "international marketing",
        ],
    },

    "economics": {
        "title": "اقتصاد",
        "queries": [
            "economics",
            "microeconomics",
            "macroeconomics",
            "managerial economics",
        ],
    },

    "human_resources": {
        "title": "مدیریت منابع انسانی",
        "queries": [
            "human resource management",
            "HRM",
            "employee performance",
            "talent management",
        ],
    },

    "artificial_intelligence": {
        "title": "هوش مصنوعی در کسب‌وکار",
        "queries": [
            "artificial intelligence business",
            "AI in management",
            "generative AI business",
            "agentic AI business",
        ],
    },

    "fintech": {
        "title": "فین‌تک و بانکداری دیجیتال",
        "queries": [
            "fintech",
            "financial technology",
            "digital banking",
            "financial innovation",
        ],
    },

    "ecommerce": {
        "title": "تجارت الکترونیک",
        "queries": [
            "e-commerce",
            "electronic commerce",
            "online business",
            "digital commerce",
        ],
    },
}


# ---------------------------------------------------------
# Educational modules
# ---------------------------------------------------------

EDUCATIONAL_MODULES = {
    "management": "مدیریت و بازرگانی",
    "banking": "بانکداری",
    "finance": "مدیریت مالی",
    "accounting": "حسابداری",
    "marketing": "بازاریابی و فروش",
    "international_business": "تجارت بین‌الملل",
    "foundations": "دروس پایه مدیریت",
    "english": "زبان انگلیسی از صفر تا پیشرفته",
}


# ---------------------------------------------------------
# Employment exam modules
# ---------------------------------------------------------

EMPLOYMENT_MODULES = {
    "general": "دروس عمومی",
    "management": "تخصصی مدیریت",
    "public_management": "مدیریت دولتی",
    "business_management": "مدیریت بازرگانی",
    "accounting": "حسابداری",
    "economics": "اقتصاد",
    "banking": "بانکداری",
    "english": "زبان انگلیسی",
    "icdl": "فناوری اطلاعات و ICDL",
    "aptitude": "هوش و استعداد",
    "mathematics": "ریاضی و آمار",
}


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

def validate_config() -> None:
    """
    Validate the minimum configuration
    required to start the bot.
    """

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN تنظیم نشده است. "
            "آن را در Environment Variables رندر وارد کنید."
        )

    if not ALLOWED_USER_IDS:
        raise RuntimeError(
            "ALLOWED_USER_IDS تنظیم نشده است. "
            "آیدی عددی تلگرام خودتان را وارد کنید."
        )


# ---------------------------------------------------------
# Startup information
# ---------------------------------------------------------

def get_config_summary() -> dict:
    """
    Safe configuration summary.

    BOT_TOKEN is intentionally never returned.
    """

    return {
        "app_name": APP_NAME,
        "bot_name": BOT_NAME,
        "database": "SQLite",
        "private_access": bool(
            ALLOWED_USER_IDS
        ),
        "allowed_users": len(
            ALLOWED_USER_IDS
        ),
        "auto_update": AUTO_UPDATE_ENABLED,
        "update_interval_hours":
            AUTO_UPDATE_INTERVAL_HOURS,
        "update_limit":
            AUTO_UPDATE_LIMIT,
        "scientific_sources":
            SCIENTIFIC_SOURCES,
        "watched_topics":
            len(WATCH_TOPICS),
    }
