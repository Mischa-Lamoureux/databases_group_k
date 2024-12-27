import psycopg2
from psycopg2.extensions import connection
from typing import Optional
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()


def connect() -> Optional[connection]:
    DB_CONFIG = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD") or None,  # Handle empty password
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Database connection successful.")
        return conn
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return None


def disconnect(conn: connection):
    if conn:
        conn.close()
        print("Disconnected from database")


def main():
    conn = connect()
    disconnect(conn)


if __name__ == "__main__":

    main()
