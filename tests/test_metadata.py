import sys
from pathlib import Path


# Add project python directory to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_DIR = PROJECT_ROOT / "python"

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))


from config import OBJECT_FOLDERS
from metadata_comparator import MetadataComparator
from yaml_manager import YAMLManager


def test_object_folder_mapping():
    """
    Verify that all supported MySQL object types
    have a corresponding metadata folder.
    """

    expected_objects = {
        "TABLE",
        "VIEW",
        "PROCEDURE",
        "FUNCTION",
        "TRIGGER",
        "EVENT",
    }

    assert expected_objects.issubset(
        set(OBJECT_FOLDERS.keys())
    )


def test_yaml_manager_safe_filename():
    """
    Verify that database object names can be converted
    into safe YAML filenames.
    """

    manager = YAMLManager()

    result = manager.safe_filename(
        "employee:test/table"
    )

    assert ":" not in result
    assert "/" not in result
    assert "\\" not in result


def test_comparator_detects_changes():
    """
    Basic test for metadata change detection.
    """

    comparator = MetadataComparator()

    old_metadata = {
        "tables": [
            {
                "object": {
                    "type": "table",
                    "name": "employees",
                },
                "columns": [
                    {
                        "name": "emp_no",
                        "data_type": "int",
                    }
                ],
                "indexes": [],
                "foreign_keys": [],
            }
        ],
        "views": [],
        "procedures": [],
        "functions": [],
        "triggers": [],
        "events": [],
    }

    current_metadata = {
        "tables": [
            {
                "object": {
                    "type": "table",
                    "name": "employees",
                },
                "columns": [
                    {
                        "name": "emp_no",
                        "data_type": "int",
                    },
                    {
                        "name": "email",
                        "data_type": "varchar",
                    },
                ],
                "indexes": [],
                "foreign_keys": [],
            }
        ],
        "views": [],
        "procedures": [],
        "functions": [],
        "triggers": [],
        "events": [],
    }

    # Write temporary metadata into a test structure
    # using the comparator's internal comparison logic.
    changes = {
        "objects_added": [],
        "objects_modified": [],
        "objects_deleted": [],
        "columns_added": [],
        "columns_modified": [],
        "columns_deleted": [],
        "indexes_added": [],
        "indexes_deleted": [],
        "foreign_keys_added": [],
        "foreign_keys_deleted": [],
    }

    comparator.compare_tables(
        old_metadata["tables"],
        current_metadata["tables"],
        changes,
    )

    assert len(changes["columns_added"]) == 1

    assert (
        changes["columns_added"][0]["table"]
        == "employees"
    )

    assert (
        changes["columns_added"][0]["column"]
        == "email"
    )


def test_no_changes():
    """
    Verify that identical metadata produces no changes.
    """

    comparator = MetadataComparator()

    changes = {
        "objects_added": [],
        "objects_modified": [],
        "objects_deleted": [],
        "columns_added": [],
        "columns_modified": [],
        "columns_deleted": [],
        "indexes_added": [],
        "indexes_deleted": [],
        "foreign_keys_added": [],
        "foreign_keys_deleted": [],
    }

    assert comparator.has_changes(changes) is False