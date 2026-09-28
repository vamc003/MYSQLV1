# MySQL Database Metadata Extractor

A lightweight Python-based solution for extracting MySQL database structure metadata and maintaining it as version-controlled YAML files in GitHub.

The project is designed to provide a clean metadata source for future LLM/RAG-based database question answering.

---

## 1. Objective

The objective of this project is to extract MySQL database object metadata without storing SQL object files or actual database records in GitHub.

The Python application connects to MySQL, extracts database structure information, generates YAML metadata files, detects structural changes, maintains historical change records, and stores the metadata in GitHub.

### Architecture

MySQL Database

↓

Python Metadata Extractor

↓

YAML Metadata

↓

Change Detection

↓

History

↓

Git

↓

GitHub

↓

Future LLM / RAG

↓

Database Metadata Question Answering

---

# 2. Key Principles

This project follows the following principles:

- MySQL remains the source of truth.
- GitHub stores database metadata only.
- No employee/business data is stored in GitHub.
- No `.sql` database object files are required.
- No database passwords or credentials are stored in GitHub.
- YAML files represent the current database structure.
- Historical changes are maintained separately.
- The architecture is simple and extensible.
- Metadata is structured for future LLM/RAG consumption.

---

# 3. Supported MySQL Objects

The extractor currently supports:

1. Database / Schema
2. Tables
3. Columns
4. Primary Keys
5. Foreign Keys
6. Unique Constraints
7. Indexes
8. Check Constraints
9. Views
10. Stored Procedures
11. Stored Functions
12. Triggers
13. Events
14. Relationships
15. Object Dependencies

Additional object types can be added later.

---

# 4. Repository Structure

```text
MYSQLV1/
│
├── README.md
│
├── database.yml
├── object-catalog.yml
├── relationships.yml
├── dependencies.yml
│
├── tables/
│   ├── employees.yml
│   ├── departments.yml
│   ├── dept_emp.yml
│   ├── dept_manager.yml
│   ├── salaries.yml
│   └── titles.yml
│
├── views/
│   └── employee_details.yml
│
├── procedures/
│   └── get_employee.yml
│
├── functions/
│   └── calculate_salary.yml
│
├── triggers/
│   └── employee_audit.yml
│
├── events/
│   └── salary_review.yml
│
├── history/
│   └── 2026/
│       ├── 2026-09-28.yml
│       └── 2026-10-05.yml
│
├── config/
│   └── metadata-config.yml
│
├── python/
│   ├── config.py
│   ├── db_connection.py
│   ├── metadata_extractor.py
│   ├── metadata_comparator.py
│   ├── yaml_manager.py
│   ├── history_manager.py
│   └── sync.py
│
├── tests/
│   └── test_metadata.py
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md