from datetime import datetime
from pathlib import Path

import yaml

from config import HISTORY_DIR, MYSQL_DATABASE


class HistoryManager:
    """
    Create historical YAML records for metadata changes.
    """

    def create_history(
        self,
        changes,
    ):

        if not self.has_changes(changes):
            return None

        now = datetime.now()

        year = str(now.year)

        date_string = now.strftime(
            "%Y-%m-%d"
        )

        history_directory = (
            HISTORY_DIR / year
        )

        history_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        history_file = (
            history_directory
            / f"{date_string}.yml"
        )

        history_data = {
            "change_set": {
                "date": date_string,
                "database": MYSQL_DATABASE,
                "generated_at": now.isoformat(),
            },
            "summary": self.create_summary(
                changes
            ),
            "changes": changes,
        }

        with open(
            history_file,
            "w",
            encoding="utf-8",
        ) as file:

            yaml.safe_dump(
                history_data,
                file,
                sort_keys=False,
                allow_unicode=True,
            )

        return history_file

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    @staticmethod
    def create_summary(changes):

        return {
            "objects_added": len(
                changes.get(
                    "objects_added",
                    [],
                )
            ),
            "objects_modified": len(
                changes.get(
                    "objects_modified",
                    [],
                )
            ),
            "objects_deleted": len(
                changes.get(
                    "objects_deleted",
                    [],
                )
            ),
            "columns_added": len(
                changes.get(
                    "columns_added",
                    [],
                )
            ),
            "columns_modified": len(
                changes.get(
                    "columns_modified",
                    [],
                )
            ),
            "columns_deleted": len(
                changes.get(
                    "columns_deleted",
                    [],
                )
            ),
            "indexes_added": len(
                changes.get(
                    "indexes_added",
                    [],
                )
            ),
            "indexes_deleted": len(
                changes.get(
                    "indexes_deleted",
                    [],
                )
            ),
            "foreign_keys_added": len(
                changes.get(
                    "foreign_keys_added",
                    [],
                )
            ),
            "foreign_keys_deleted": len(
                changes.get(
                    "foreign_keys_deleted",
                    [],
                )
            ),
        }

    # ---------------------------------------------------------
    # CHECK
    # ---------------------------------------------------------

    @staticmethod
    def has_changes(changes):

        return any(
            bool(value)
            for value in changes.values()
        )