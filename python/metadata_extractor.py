from db_connection import fetch_all, fetch_one
from config import MYSQL_DATABASE


class MetadataExtractor:
    """
    Extract MySQL database structure metadata.

    This class never extracts business/employee data.
    It extracts database definition metadata only.
    """

    def extract_all(self):
        """
        Extract all supported database metadata.
        """

        metadata = {
            "database": self.extract_database(),
            "tables": self.extract_tables(),
            "views": self.extract_views(),
            "procedures": self.extract_procedures(),
            "functions": self.extract_functions(),
            "triggers": self.extract_triggers(),
            "events": self.extract_events(),
            "relationships": self.extract_relationships(),
            "dependencies": self.extract_dependencies(),
        }

        return metadata

    # ---------------------------------------------------------
    # DATABASE
    # ---------------------------------------------------------

    def extract_database(self):
        query = """
            SELECT
                SCHEMA_NAME AS database_name,
                DEFAULT_CHARACTER_SET_NAME AS character_set,
                DEFAULT_COLLATION_NAME AS collation
            FROM information_schema.SCHEMATA
            WHERE SCHEMA_NAME = %s
        """

        row = fetch_one(query, (MYSQL_DATABASE,))

        return row or {
            "database_name": MYSQL_DATABASE
        }

    # ---------------------------------------------------------
    # TABLES
    # ---------------------------------------------------------

    def extract_tables(self):
        query = """
            SELECT
                TABLE_NAME,
                ENGINE,
                TABLE_COLLATION,
                TABLE_COMMENT
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s
              AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """

        tables = fetch_all(query, (MYSQL_DATABASE,))

        result = []

        for table in tables:

            table_name = table["TABLE_NAME"]

            table_metadata = {
                "object": {
                    "type": "table",
                    "name": table_name,
                },
                "metadata": {
                    "engine": table["ENGINE"],
                    "collation": table["TABLE_COLLATION"],
                    "comment": table["TABLE_COMMENT"],
                },
                "columns": self.extract_columns(table_name),
                "primary_key": self.extract_primary_key(table_name),
                "foreign_keys": self.extract_foreign_keys(table_name),
                "unique_constraints": self.extract_unique_constraints(
                    table_name
                ),
                "indexes": self.extract_indexes(table_name),
                "check_constraints": self.extract_check_constraints(
                    table_name
                ),
            }

            result.append(table_metadata)

        return result

    # ---------------------------------------------------------
    # COLUMNS
    # ---------------------------------------------------------

    def extract_columns(self, table_name):

        query = """
            SELECT
                ORDINAL_POSITION,
                COLUMN_NAME,
                DATA_TYPE,
                COLUMN_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                EXTRA,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE, table_name),
        )

        columns = []

        for row in rows:

            columns.append(
                {
                    "name": row["COLUMN_NAME"],
                    "position": row["ORDINAL_POSITION"],
                    "data_type": row["DATA_TYPE"],
                    "column_type": row["COLUMN_TYPE"],
                    "length": row["CHARACTER_MAXIMUM_LENGTH"],
                    "precision": row["NUMERIC_PRECISION"],
                    "scale": row["NUMERIC_SCALE"],
                    "nullable": row["IS_NULLABLE"] == "YES",
                    "default": row["COLUMN_DEFAULT"],
                    "extra": row["EXTRA"],
                    "comment": row["COLUMN_COMMENT"],
                }
            )

        return columns

    # ---------------------------------------------------------
    # PRIMARY KEY
    # ---------------------------------------------------------

    def extract_primary_key(self, table_name):

        query = """
            SELECT
                COLUMN_NAME,
                ORDINAL_POSITION
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME = %s
              AND CONSTRAINT_NAME = 'PRIMARY'
            ORDER BY ORDINAL_POSITION
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE, table_name),
        )

        return {
            "columns": [
                row["COLUMN_NAME"]
                for row in rows
            ]
        }

    # ---------------------------------------------------------
    # FOREIGN KEYS
    # ---------------------------------------------------------

    def extract_foreign_keys(self, table_name):

        query = """
            SELECT
                kcu.CONSTRAINT_NAME,
                kcu.COLUMN_NAME,
                kcu.REFERENCED_TABLE_NAME,
                kcu.REFERENCED_COLUMN_NAME,
                rc.UPDATE_RULE,
                rc.DELETE_RULE
            FROM information_schema.KEY_COLUMN_USAGE kcu
            LEFT JOIN information_schema.REFERENTIAL_CONSTRAINTS rc
                ON kcu.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA
                AND kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
                AND kcu.TABLE_NAME = rc.TABLE_NAME
            WHERE kcu.TABLE_SCHEMA = %s
              AND kcu.TABLE_NAME = %s
              AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
            ORDER BY kcu.CONSTRAINT_NAME, kcu.ORDINAL_POSITION
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE, table_name),
        )

        foreign_keys = {}

        for row in rows:

            constraint_name = row["CONSTRAINT_NAME"]

            if constraint_name not in foreign_keys:
                foreign_keys[constraint_name] = {
                    "name": constraint_name,
                    "columns": [],
                    "referenced_table": row[
                        "REFERENCED_TABLE_NAME"
                    ],
                    "referenced_columns": [],
                    "update_rule": row["UPDATE_RULE"],
                    "delete_rule": row["DELETE_RULE"],
                }

            foreign_keys[constraint_name]["columns"].append(
                row["COLUMN_NAME"]
            )

            foreign_keys[constraint_name][
                "referenced_columns"
            ].append(
                row["REFERENCED_COLUMN_NAME"]
            )

        return list(foreign_keys.values())

    # ---------------------------------------------------------
    # UNIQUE CONSTRAINTS
    # ---------------------------------------------------------

    def extract_unique_constraints(self, table_name):

        query = """
            SELECT
                tc.CONSTRAINT_NAME,
                kcu.COLUMN_NAME,
                kcu.ORDINAL_POSITION
            FROM information_schema.TABLE_CONSTRAINTS tc
            JOIN information_schema.KEY_COLUMN_USAGE kcu
                ON tc.CONSTRAINT_SCHEMA = kcu.CONSTRAINT_SCHEMA
                AND tc.TABLE_NAME = kcu.TABLE_NAME
                AND tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            WHERE tc.TABLE_SCHEMA = %s
              AND tc.TABLE_NAME = %s
              AND tc.CONSTRAINT_TYPE = 'UNIQUE'
            ORDER BY tc.CONSTRAINT_NAME, kcu.ORDINAL_POSITION
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE, table_name),
        )

        constraints = {}

        for row in rows:

            name = row["CONSTRAINT_NAME"]

            constraints.setdefault(
                name,
                {
                    "name": name,
                    "columns": [],
                },
            )

            constraints[name]["columns"].append(
                row["COLUMN_NAME"]
            )

        return list(constraints.values())

    # ---------------------------------------------------------
    # INDEXES
    # ---------------------------------------------------------

    def extract_indexes(self, table_name):

        query = """
            SELECT
                INDEX_NAME,
                NON_UNIQUE,
                COLUMN_NAME,
                SEQ_IN_INDEX,
                INDEX_TYPE
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME = %s
              AND INDEX_NAME <> 'PRIMARY'
            ORDER BY INDEX_NAME, SEQ_IN_INDEX
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE, table_name),
        )

        indexes = {}

        for row in rows:

            name = row["INDEX_NAME"]

            indexes.setdefault(
                name,
                {
                    "name": name,
                    "unique": row["NON_UNIQUE"] == 0,
                    "type": row["INDEX_TYPE"],
                    "columns": [],
                },
            )

            indexes[name]["columns"].append(
                row["COLUMN_NAME"]
            )

        return list(indexes.values())

    # ---------------------------------------------------------
    # CHECK CONSTRAINTS
    # ---------------------------------------------------------

    def extract_check_constraints(self, table_name):

        query = """
            SELECT
                CONSTRAINT_NAME,
                CHECK_CLAUSE
            FROM information_schema.CHECK_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = %s
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE,),
        )

        constraints = []

        for row in rows:

            constraints.append(
                {
                    "name": row["CONSTRAINT_NAME"],
                    "expression": row["CHECK_CLAUSE"],
                }
            )

        return constraints

    # ---------------------------------------------------------
    # VIEWS
    # ---------------------------------------------------------

    def extract_views(self):

        query = """
            SELECT
                TABLE_NAME,
                VIEW_DEFINITION,
                CHECK_OPTION,
                IS_UPDATABLE
            FROM information_schema.VIEWS
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE,),
        )

        return [
            {
                "object": {
                    "type": "view",
                    "name": row["TABLE_NAME"],
                },
                "definition": row["VIEW_DEFINITION"],
                "check_option": row["CHECK_OPTION"],
                "updatable": row["IS_UPDATABLE"],
            }
            for row in rows
        ]

    # ---------------------------------------------------------
    # PROCEDURES
    # ---------------------------------------------------------

    def extract_procedures(self):

        query = """
            SELECT
                ROUTINE_NAME,
                ROUTINE_DEFINITION,
                DTD_IDENTIFIER,
                SQL_DATA_ACCESS,
                IS_DETERMINISTIC,
                SECURITY_TYPE
            FROM information_schema.ROUTINES
            WHERE ROUTINE_SCHEMA = %s
              AND ROUTINE_TYPE = 'PROCEDURE'
            ORDER BY ROUTINE_NAME
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE,),
        )

        return [
            {
                "object": {
                    "type": "procedure",
                    "name": row["ROUTINE_NAME"],
                },
                "definition": row["ROUTINE_DEFINITION"],
                "return_type": row["DTD_IDENTIFIER"],
                "sql_data_access": row["SQL_DATA_ACCESS"],
                "deterministic": row["IS_DETERMINISTIC"],
                "security_type": row["SECURITY_TYPE"],
            }
            for row in rows
        ]

    # ---------------------------------------------------------
    # FUNCTIONS
    # ---------------------------------------------------------

    def extract_functions(self):

        query = """
            SELECT
                ROUTINE_NAME,
                ROUTINE_DEFINITION,
                DTD_IDENTIFIER,
                SQL_DATA_ACCESS,
                IS_DETERMINISTIC,
                SECURITY_TYPE
            FROM information_schema.ROUTINES
            WHERE ROUTINE_SCHEMA = %s
              AND ROUTINE_TYPE = 'FUNCTION'
            ORDER BY ROUTINE_NAME
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE,),
        )

        return [
            {
                "object": {
                    "type": "function",
                    "name": row["ROUTINE_NAME"],
                },
                "definition": row["ROUTINE_DEFINITION"],
                "return_type": row["DTD_IDENTIFIER"],
                "sql_data_access": row["SQL_DATA_ACCESS"],
                "deterministic": row["IS_DETERMINISTIC"],
                "security_type": row["SECURITY_TYPE"],
            }
            for row in rows
        ]

    # ---------------------------------------------------------
    # TRIGGERS
    # ---------------------------------------------------------

    def extract_triggers(self):

        query = """
            SELECT
                TRIGGER_NAME,
                EVENT_MANIPULATION,
                EVENT_OBJECT_TABLE,
                ACTION_TIMING,
                ACTION_STATEMENT,
                ACTION_ORIENTATION
            FROM information_schema.TRIGGERS
            WHERE TRIGGER_SCHEMA = %s
            ORDER BY TRIGGER_NAME
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE,),
        )

        return [
            {
                "object": {
                    "type": "trigger",
                    "name": row["TRIGGER_NAME"],
                },
                "event": row["EVENT_MANIPULATION"],
                "table": row["EVENT_OBJECT_TABLE"],
                "timing": row["ACTION_TIMING"],
                "statement": row["ACTION_STATEMENT"],
                "orientation": row["ACTION_ORIENTATION"],
            }
            for row in rows
        ]

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------

    def extract_events(self):

        query = """
            SELECT
                EVENT_NAME,
                EVENT_DEFINITION,
                EVENT_TYPE,
                EXECUTE_AT,
                INTERVAL_VALUE,
                INTERVAL_FIELD,
                STATUS,
                EVENT_COMMENT
            FROM information_schema.EVENTS
            WHERE EVENT_SCHEMA = %s
            ORDER BY EVENT_NAME
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE,),
        )

        return [
            {
                "object": {
                    "type": "event",
                    "name": row["EVENT_NAME"],
                },
                "definition": row["EVENT_DEFINITION"],
                "event_type": row["EVENT_TYPE"],
                "execute_at": row["EXECUTE_AT"],
                "interval_value": row["INTERVAL_VALUE"],
                "interval_field": row["INTERVAL_FIELD"],
                "status": row["STATUS"],
                "comment": row["EVENT_COMMENT"],
            }
            for row in rows
        ]

    # ---------------------------------------------------------
    # RELATIONSHIPS
    # ---------------------------------------------------------

    def extract_relationships(self):

        query = """
            SELECT
                TABLE_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME,
                CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s
              AND REFERENCED_TABLE_NAME IS NOT NULL
            ORDER BY TABLE_NAME, CONSTRAINT_NAME
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE,),
        )

        return [
            {
                "from_table": row["TABLE_NAME"],
                "from_column": row["COLUMN_NAME"],
                "to_table": row["REFERENCED_TABLE_NAME"],
                "to_column": row["REFERENCED_COLUMN_NAME"],
                "constraint": row["CONSTRAINT_NAME"],
            }
            for row in rows
        ]

    # ---------------------------------------------------------
    # DEPENDENCIES
    # ---------------------------------------------------------

    def extract_dependencies(self):

        query = """
            SELECT
                TABLE_NAME AS dependent_object,
                REFERENCED_TABLE_NAME AS referenced_object
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s
              AND REFERENCED_TABLE_NAME IS NOT NULL
        """

        rows = fetch_all(
            query,
            (MYSQL_DATABASE,),
        )

        return [
            {
                "dependent": row["dependent_object"],
                "depends_on": row["referenced_object"],
            }
            for row in rows
        ]