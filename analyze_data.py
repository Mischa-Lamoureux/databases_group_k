import psycopg2
from psycopg2.extensions import connection
from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt
import mplcyberpunk
from dotenv import load_dotenv
import os

load_dotenv()
plt.style.use("cyberpunk")


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


def get_country_medals_over_time(conn: connection):
    query = """
    SELECT
        c.name AS country,
        g.year,
        COUNT(r.result_id) AS total_medals
    FROM result r
    JOIN game g ON r.game_id = g.game_id
    JOIN athlete a ON r.athlete_id = a.athlete_id
    JOIN country c ON a.country_id = c.country_id
    WHERE r.position IN ('1', '2', '3')
    GROUP BY c.name, g.year
    ORDER BY g.year, total_medals DESC;
    """

    df_medals = pd.read_sql_query(query, conn)
    if not df_medals.empty:
        pivot_df = df_medals.pivot(
            index="year", columns="country", values="total_medals"
        ).fillna(0)
        pivot_df.plot(figsize=(12, 8))
        plt.title("Olympic Medals by Country Over Time")
        plt.xlabel("Year")
        plt.ylabel("Number of Medals")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.show()


def main():
    conn = connect()
    get_country_medals_over_time(conn)
    disconnect(conn)


if __name__ == "__main__":

    main()


# POTENTIAL PLOTS

# - Change in Olympic Success Over Time by Country
# - Relationship Between Success and Athlete Count Per Country Over Time
# - Impact of Gender Ratio on Success
# - Average Age of Athletes vs. Medal Success
# - Host Country Advantage in Medal Count
