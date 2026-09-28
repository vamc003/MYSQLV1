import mysql.connector

from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
)


def get_connection():
    """
    Create and return a MySQL database connection.
    """

    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )

    return connection


def fetch_all(query, params=None):
    """
    Execute a SELECT query and return all rows as dictionaries.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, params or ())

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def fetch_one(query, params=None):
    """
    Execute a SELECT query and return one row.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, params or ())

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()