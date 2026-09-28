import sys
from pathlib import Path

# Add python directory to import path
PYTHON_DIR = Path(__file__).resolve().parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(PYTHON_DIR),
    )


from config import (
    PROJECT_ROOT,
    create_directories,
    validate_config,
    MYSQL_DATABASE,
)

from db_connection import get_connection
from metadata_extractor import MetadataExtractor
from metadata_comparator import MetadataComparator
from yaml_manager import YAMLManager
from history_manager import HistoryManager


def main():

    print("=" * 70)
    print("MYSQL DATABASE METADATA SYNC")
    print("=" * 70)

    try:

        # -----------------------------------------------------
        # 1. Validate configuration
        # -----------------------------------------------------

        print("\n[1/7] Validating configuration...")

        validate_config()
        create_directories()

        print("Configuration OK.")

        # -----------------------------------------------------
        # 2. Test database connection
        # -----------------------------------------------------

        print("\n[2/7] Connecting to MySQL...")

        connection = get_connection()

        print(
            f"Connected to database: "
            f"{MYSQL_DATABASE}"
        )

        connection.close()

        # -----------------------------------------------------
        # 3. Extract metadata
        # -----------------------------------------------------

        print("\n[3/7] Extracting database metadata...")

        extractor = MetadataExtractor()

        current_metadata = (
            extractor.extract_all()
        )

        print(
            f"Tables: "
            f"{len(current_metadata['tables'])}"
        )

        print(
            f"Views: "
            f"{len(current_metadata['views'])}"
        )

        print(
            f"Procedures: "
            f"{len(current_metadata['procedures'])}"
        )

        print(
            f"Functions: "
            f"{len(current_metadata['functions'])}"
        )

        print(
            f"Triggers: "
            f"{len(current_metadata['triggers'])}"
        )

        print(
            f"Events: "
            f"{len(current_metadata['events'])}"
        )

        # -----------------------------------------------------
        # 4. Compare metadata
        # -----------------------------------------------------

        print("\n[4/7] Comparing metadata...")

        comparator = MetadataComparator()

        changes = comparator.compare(
            current_metadata,
            PROJECT_ROOT,
        )

        if comparator.has_changes(changes):

            print("Changes detected.")

        else:

            print(
                "No metadata changes detected."
            )

        # -----------------------------------------------------
        # 5. Update YAML metadata
        # -----------------------------------------------------

        print("\n[5/7] Updating YAML metadata...")

        yaml_manager = YAMLManager()

        yaml_manager.write_metadata(
            current_metadata
        )

        print(
            "YAML metadata updated successfully."
        )

        # -----------------------------------------------------
        # 6. Generate history
        # -----------------------------------------------------

        print("\n[6/7] Processing history...")

        history_manager = HistoryManager()

        history_file = (
            history_manager.create_history(
                changes
            )
        )

        if history_file:

            print(
                f"History created: "
                f"{history_file}"
            )

        else:

            print(
                "No history required."
            )

        # -----------------------------------------------------
        # 7. Finish
        # -----------------------------------------------------

        print("\n[7/7] Synchronization completed.")

        print("\nRepository:")
        print(PROJECT_ROOT)

        print("\nMetadata synchronization completed successfully.")

        return 0

    except Exception as error:

        print("\nERROR:")
        print(str(error))

        return 1


if __name__ == "__main__":

    sys.exit(main())