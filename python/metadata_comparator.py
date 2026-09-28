from pathlib import Path

import yaml


class MetadataComparator:
    """
    Compare existing YAML metadata with current MySQL metadata.
    """

    def compare(self, current_metadata, repository_root):
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

        old_metadata = self.load_existing_metadata(
            repository_root
        )

        self.compare_tables(
            old_metadata.get("tables", []),
            current_metadata.get("tables", []),
            changes,
        )

        self.compare_object_type(
            "views",
            old_metadata,
            current_metadata,
            changes,
        )

        self.compare_object_type(
            "procedures",
            old_metadata,
            current_metadata,
            changes,
        )

        self.compare_object_type(
            "functions",
            old_metadata,
            current_metadata,
            changes,
        )

        self.compare_object_type(
            "triggers",
            old_metadata,
            current_metadata,
            changes,
        )

        self.compare_object_type(
            "events",
            old_metadata,
            current_metadata,
            changes,
        )

        return changes

    # ---------------------------------------------------------
    # LOAD EXISTING YAML
    # ---------------------------------------------------------

    def load_existing_metadata(self, repository_root):

        metadata = {
            "tables": [],
            "views": [],
            "procedures": [],
            "functions": [],
            "triggers": [],
            "events": [],
        }

        folders = {
            "tables": "tables",
            "views": "views",
            "procedures": "procedures",
            "functions": "functions",
            "triggers": "triggers",
            "events": "events",
        }

        for object_type, folder in folders.items():

            directory = Path(repository_root) / folder

            if not directory.exists():
                continue

            for file in directory.glob("*.yml"):

                with open(
                    file,
                    "r",
                    encoding="utf-8",
                ) as stream:

                    data = yaml.safe_load(stream) or {}

                    metadata[object_type].append(data)

        return metadata

    # ---------------------------------------------------------
    # TABLE COMPARISON
    # ---------------------------------------------------------

    def compare_tables(
        self,
        old_tables,
        current_tables,
        changes,
    ):

        old_map = {
            item["object"]["name"]: item
            for item in old_tables
            if "object" in item
        }

        current_map = {
            item["object"]["name"]: item
            for item in current_tables
            if "object" in item
        }

        old_names = set(old_map)
        current_names = set(current_map)

        # New tables
        for table_name in current_names - old_names:

            changes["objects_added"].append(
                {
                    "type": "table",
                    "name": table_name,
                }
            )

        # Deleted tables
        for table_name in old_names - current_names:

            changes["objects_deleted"].append(
                {
                    "type": "table",
                    "name": table_name,
                }
            )

        # Existing tables
        for table_name in current_names & old_names:

            old_table = old_map[table_name]
            current_table = current_map[table_name]

            self.compare_columns(
                table_name,
                old_table.get("columns", []),
                current_table.get("columns", []),
                changes,
            )

            self.compare_indexes(
                table_name,
                old_table.get("indexes", []),
                current_table.get("indexes", []),
                changes,
            )

            self.compare_foreign_keys(
                table_name,
                old_table.get("foreign_keys", []),
                current_table.get("foreign_keys", []),
                changes,
            )

            if old_table != current_table:

                changes["objects_modified"].append(
                    {
                        "type": "table",
                        "name": table_name,
                    }
                )

    # ---------------------------------------------------------
    # COLUMNS
    # ---------------------------------------------------------

    def compare_columns(
        self,
        table_name,
        old_columns,
        current_columns,
        changes,
    ):

        old_map = {
            column["name"]: column
            for column in old_columns
        }

        current_map = {
            column["name"]: column
            for column in current_columns
        }

        old_names = set(old_map)
        current_names = set(current_map)

        for name in current_names - old_names:

            changes["columns_added"].append(
                {
                    "table": table_name,
                    "column": name,
                }
            )

        for name in old_names - current_names:

            changes["columns_deleted"].append(
                {
                    "table": table_name,
                    "column": name,
                }
            )

        for name in current_names & old_names:

            if old_map[name] != current_map[name]:

                changes["columns_modified"].append(
                    {
                        "table": table_name,
                        "column": name,
                    }
                )

    # ---------------------------------------------------------
    # INDEXES
    # ---------------------------------------------------------

    def compare_indexes(
        self,
        table_name,
        old_indexes,
        current_indexes,
        changes,
    ):

        old_map = {
            index["name"]: index
            for index in old_indexes
        }

        current_map = {
            index["name"]: index
            for index in current_indexes
        }

        for name in current_map.keys() - old_map.keys():

            changes["indexes_added"].append(
                {
                    "table": table_name,
                    "index": name,
                }
            )

        for name in old_map.keys() - current_map.keys():

            changes["indexes_deleted"].append(
                {
                    "table": table_name,
                    "index": name,
                }
            )

    # ---------------------------------------------------------
    # FOREIGN KEYS
    # ---------------------------------------------------------

    def compare_foreign_keys(
        self,
        table_name,
        old_keys,
        current_keys,
        changes,
    ):

        old_map = {
            key["name"]: key
            for key in old_keys
        }

        current_map = {
            key["name"]: key
            for key in current_keys
        }

        for name in current_map.keys() - old_map.keys():

            changes["foreign_keys_added"].append(
                {
                    "table": table_name,
                    "foreign_key": name,
                }
            )

        for name in old_map.keys() - current_map.keys():

            changes["foreign_keys_deleted"].append(
                {
                    "table": table_name,
                    "foreign_key": name,
                }
            )

    # ---------------------------------------------------------
    # OTHER OBJECT TYPES
    # ---------------------------------------------------------

    def compare_object_type(
        self,
        object_type,
        old_metadata,
        current_metadata,
        changes,
    ):

        old_objects = {
            item["object"]["name"]: item
            for item in old_metadata.get(
                object_type,
                [],
            )
            if "object" in item
        }

        current_objects = {
            item["object"]["name"]: item
            for item in current_metadata.get(
                object_type,
                [],
            )
            if "object" in item
        }

        for name in current_objects.keys() - old_objects.keys():

            changes["objects_added"].append(
                {
                    "type": object_type[:-1],
                    "name": name,
                }
            )

        for name in old_objects.keys() - current_objects.keys():

            changes["objects_deleted"].append(
                {
                    "type": object_type[:-1],
                    "name": name,
                }
            )

        for name in current_objects.keys() & old_objects.keys():

            if old_objects[name] != current_objects[name]:

                changes["objects_modified"].append(
                    {
                        "type": object_type[:-1],
                        "name": name,
                    }
                )

    # ---------------------------------------------------------
    # CHECK WHETHER CHANGES EXIST
    # ---------------------------------------------------------

    @staticmethod
    def has_changes(changes):

        return any(
            bool(value)
            for value in changes.values()
        )