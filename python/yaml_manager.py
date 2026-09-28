from pathlib import Path

import yaml

from config import (
    DATABASE_FILE,
    OBJECT_CATALOG_FILE,
    RELATIONSHIPS_FILE,
    DEPENDENCIES_FILE,
    OBJECT_FOLDERS,
)


class YAMLManager:
    """
    Create and maintain YAML metadata files.
    """

    def write_metadata(
        self,
        metadata,
    ):

        self.write_database(
            metadata.get("database", {})
        )

        self.write_object_files(
            metadata
        )

        self.write_relationships(
            metadata.get("relationships", [])
        )

        self.write_dependencies(
            metadata.get("dependencies", [])
        )

        self.write_object_catalog(
            metadata
        )

    # ---------------------------------------------------------
    # DATABASE
    # ---------------------------------------------------------

    def write_database(self, database):

        data = {
            "database": database
        }

        self.write_yaml(
            DATABASE_FILE,
            data,
        )

    # ---------------------------------------------------------
    # OBJECT FILES
    # ---------------------------------------------------------

    def write_object_files(self, metadata):

        object_mapping = {
            "tables": "TABLE",
            "views": "VIEW",
            "procedures": "PROCEDURE",
            "functions": "FUNCTION",
            "triggers": "TRIGGER",
            "events": "EVENT",
        }

        for metadata_key, object_type in object_mapping.items():

            objects = metadata.get(
                metadata_key,
                [],
            )

            folder = OBJECT_FOLDERS[object_type]

            folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            for obj in objects:

                object_name = obj[
                    "object"
                ][
                    "name"
                ]

                filename = self.safe_filename(
                    object_name
                )

                file_path = (
                    folder / f"{filename}.yml"
                )

                self.write_yaml(
                    file_path,
                    obj,
                )

    # ---------------------------------------------------------
    # RELATIONSHIPS
    # ---------------------------------------------------------

    def write_relationships(
        self,
        relationships,
    ):

        data = {
            "relationships": relationships
        }

        self.write_yaml(
            RELATIONSHIPS_FILE,
            data,
        )

    # ---------------------------------------------------------
    # DEPENDENCIES
    # ---------------------------------------------------------

    def write_dependencies(
        self,
        dependencies,
    ):

        data = {
            "dependencies": dependencies
        }

        self.write_yaml(
            DEPENDENCIES_FILE,
            data,
        )

    # ---------------------------------------------------------
    # OBJECT CATALOG
    # ---------------------------------------------------------

    def write_object_catalog(
        self,
        metadata,
    ):

        catalog = []

        mappings = {
            "tables": "tables",
            "views": "views",
            "procedures": "procedures",
            "functions": "functions",
            "triggers": "triggers",
            "events": "events",
        }

        for object_type, folder in mappings.items():

            for obj in metadata.get(
                object_type,
                [],
            ):

                name = obj[
                    "object"
                ][
                    "name"
                ]

                catalog.append(
                    {
                        "id": f"{object_type[:-1]}.{name}",
                        "type": object_type[:-1],
                        "name": name,
                        "path": (
                            f"{folder}/"
                            f"{self.safe_filename(name)}.yml"
                        ),
                    }
                )

        catalog.sort(
            key=lambda item: (
                item["type"],
                item["name"],
            )
        )

        self.write_yaml(
            OBJECT_CATALOG_FILE,
            {
                "objects": catalog
            },
        )

    # ---------------------------------------------------------
    # WRITE YAML
    # ---------------------------------------------------------

    @staticmethod
    def write_yaml(
        file_path,
        data,
    ):

        Path(file_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as file:

            yaml.safe_dump(
                data,
                file,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
            )

    # ---------------------------------------------------------
    # SAFE FILE NAME
    # ---------------------------------------------------------

    @staticmethod
    def safe_filename(name):

        invalid_characters = (
            '<>:"/\\|?*'
        )

        result = name

        for char in invalid_characters:
            result = result.replace(
                char,
                "_",
            )

        return result.strip()