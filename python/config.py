import os
from pathlib import Path

from dotenv import load_dotenv


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")


# MySQL configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")


# Repository folders
TABLES_DIR = PROJECT_ROOT / "tables"
VIEWS_DIR = PROJECT_ROOT / "views"
PROCEDURES_DIR = PROJECT_ROOT / "procedures"
FUNCTIONS_DIR = PROJECT_ROOT / "functions"
TRIGGERS_DIR = PROJECT_ROOT / "triggers"
EVENTS_DIR = PROJECT_ROOT / "events"

HISTORY_DIR = PROJECT_ROOT / "history"
CONFIG_DIR = PROJECT_ROOT / "config"


# Root metadata files
DATABASE_FILE = PROJECT_ROOT / "database.yml"
OBJECT_CATALOG_FILE = PROJECT_ROOT / "object-catalog.yml"
RELATIONSHIPS_FILE = PROJECT_ROOT / "relationships.yml"
DEPENDENCIES_FILE = PROJECT_ROOT / "dependencies.yml"


# Metadata configuration
METADATA_CONFIG_FILE = CONFIG_DIR / "metadata-config.yml"


OBJECT_FOLDERS = {
    "TABLE": TABLES_DIR,
    "VIEW": VIEWS_DIR,
    "PROCEDURE": PROCEDURES_DIR,
    "FUNCTION": FUNCTIONS_DIR,
    "TRIGGER": TRIGGERS_DIR,
    "EVENT": EVENTS_DIR,
}


def validate_config():
    """
    Validate mandatory configuration values.
    """

    missing = []

    if not MYSQL_USER:
        missing.append("MYSQL_USER")

    if not MYSQL_DATABASE:
        missing.append("MYSQL_DATABASE")

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )


def create_directories():
    """
    Create metadata directories if they do not exist.
    """

    directories = [
        TABLES_DIR,
        VIEWS_DIR,
        PROCEDURES_DIR,
        FUNCTIONS_DIR,
        TRIGGERS_DIR,
        EVENTS_DIR,
        HISTORY_DIR,
        CONFIG_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)