import os

# Set explicit paths to Tcl and Tk libraries - (delete later)
os.add_dll_directory(r"C:\Program Files\PostgreSQL\17\bin")
os.environ["TCL_LIBRARY"] = (
    r"C:\Users\grass\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"
)
os.environ["TK_LIBRARY"] = (
    r"C:\Users\grass\AppData\Local\Programs\Python\Python313\tcl\tk8.6"
)

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2


class DBConfig:
    HOST = "localhost"
    PORT = "5432"
    DB_NAME = "olympic_games_history"
    USERNAME = "postgres"
    PASSWORD = "hello"


# connect to DB
def connect_to_db(config_params):
    return psycopg2.connect(
        host=config_params.HOST,
        port=config_params.PORT,
        dbname=config_params.DB_NAME,
        user=config_params.USERNAME,
        password=config_params.PASSWORD,
    )


# function for plotting
def get_country_medals_over_time(conn):
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
    print(df_medals.head())
    print(df_medals[df_medals["year"] == 2022])
    plt.plot(df_medals["country"][0], df_medals["total_medals"][0])
    plt.show()
    """
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
    """


def get_table_with_calculated_age(conn):
    """
    Returns a pandas DataFrame with calculated ages of the athletes.
    When the start_date is missing, 01-01-XXXX or 07.01.XXXX (MM-DD-YYYY) is taken for calculation for
    winter/summer games.

     Args:
    - conn: Database connection object.
    """

    query = """
    SELECT a.date_of_birth, a.name, a.gender, r.position, game.title,
	AGE(
		CASE
            WHEN game.start_date IS NOT NULL THEN game.start_date 
			WHEN game.title ILIKE '%Wint%' THEN TO_DATE(game.year || '-01-01', 'YYYY-MM-DD') 
        	WHEN game.title ILIKE '%Sum%' THEN TO_DATE(game.year || '-07-01', 'YYYY-MM-DD')
            ELSE NULL END,
			a.date_of_birth
    ) AS age
	FROM athlete AS a
	INNER JOIN result AS r ON a.athlete_id = r.athlete_id
	INNER JOIN game ON r.game_id = game.game_id
    """

    # creating a pandas DataFrame from SQL query above and doing some preprocessing
    df_athletes = pd.read_sql_query(query, conn)
    df_athletes = df_athletes.dropna(subset=["age"])  # drop rows without age
    df_athletes["year"] = (
        df_athletes["title"].str.extract(r"(\d{4})").astype(int)
    )  # create column for year from game title
    df_athletes["game_season"] = df_athletes["title"].str.extract(
        r"(Summer|Winter)"
    )  # create column for winter / summer
    df_athletes["age"] = (
        df_athletes["age"].dt.days / 365
    )  # format age column from days to years

    # creating some filters for position, winter/summer games and gender
    gold_medalist = df_athletes["position"] == "1"
    silver_medalist = df_athletes["position"] == "2"
    bronze_medalist = df_athletes["position"] == "3"
    summer_games = df_athletes["game_season"] == "Summer"
    winter_games = df_athletes["game_season"] == "Winter"
    filter_male = df_athletes["gender"] == "Male"
    filter_female = df_athletes["gender"] == "Female"

    # calculating average ages grouped by the year of the game and creating different DataFrames for plotting later
    # (all gender) summer games gold, silver, bronze:
    av_age_gold_medalists_summer_all = (
        df_athletes[gold_medalist & summer_games]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="gold_avg_age")
    )

    av_age_silver_medalists_summer_all = (
        df_athletes[silver_medalist & summer_games]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="silver_avg_age")
    )

    av_age_bronze_medalists_summer_all = (
        df_athletes[bronze_medalist & summer_games]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="bronze_avg_age")
    )

    # (all gender) winter games gold, silver, bronze:
    av_age_gold_medalists_winter_all = (
        df_athletes[gold_medalist & winter_games]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="gold_avg_age")
    )

    av_age_silver_medalists_winter_all = (
        df_athletes[silver_medalist & winter_games]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="silver_avg_age")
    )

    av_age_bronze_medalists_winter_all = (
        df_athletes[bronze_medalist & winter_games]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="bronze_avg_age")
    )

    # --------------------------------------------------------------------------------------#
    # ----- Plot Average Age of Medal Winners of Summer Games (1896-2020 All Genders) ------#
    # --------------------------------------------------------------------------------------#

    fig, axs = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    # summer games plot
    axs[0].set_facecolor("black")  # background color
    axs[0].patch.set_alpha(0.1)
    # data
    axs[0].plot(
        av_age_gold_medalists_summer_all["year"],
        av_age_gold_medalists_summer_all["gold_avg_age"],
        label="Gold",
        color="gold",
    )
    axs[0].plot(
        av_age_silver_medalists_summer_all["year"],
        av_age_silver_medalists_summer_all["silver_avg_age"],
        label="Silver",
        color="silver",
    )
    axs[0].plot(
        av_age_bronze_medalists_summer_all["year"],
        av_age_bronze_medalists_summer_all["bronze_avg_age"],
        label="Bronze",
        color="brown",
    )
    # labelings
    axs[0].set_title(
        "[Olympic Summer Games] Average Age Medalist Winners from 1896-2020"
    )
    axs[0].set_ylabel("Average Age")
    axs[0].set_ylim([22, 32])
    axs[0].legend()
    axs[0].grid(True)

    # winter games plot
    axs[1].set_facecolor("blue")  # background color
    axs[1].patch.set_alpha(0.1)
    # data
    axs[1].plot(
        av_age_gold_medalists_winter_all["year"],
        av_age_gold_medalists_winter_all["gold_avg_age"],
        label="Gold",
        color="gold",
    )
    axs[1].plot(
        av_age_silver_medalists_winter_all["year"],
        av_age_silver_medalists_winter_all["silver_avg_age"],
        label="Silver",
        color="silver",
    )
    axs[1].plot(
        av_age_bronze_medalists_winter_all["year"],
        av_age_bronze_medalists_winter_all["bronze_avg_age"],
        label="Bronze",
        color="brown",
    )
    # labelings
    axs[1].set_title(
        "[Olympic Winter Games] Average Age of Medalist Winners from 1924-2020"
    )
    axs[1].set_xlabel("Year")
    axs[1].set_ylabel("Average Age")
    axs[1].set_ylim([22, 32])
    axs[1].legend()
    axs[1].grid(True)

    # -------------------------------------#
    # -- Male and Female Medalists AV Age--#
    # -------------------------------------#

    # Creating dfs for plotting:
    male_medalist_summer_avg_age = (
        df_athletes[
            (gold_medalist | silver_medalist | bronze_medalist)
            & summer_games
            & filter_male
        ]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="male_avg_age")
    )

    male_medalist_winter_avg_age = (
        df_athletes[
            (gold_medalist | silver_medalist | bronze_medalist)
            & winter_games
            & filter_male
        ]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="male_avg_age")
    )

    female_medalist_summer_avg_age = (
        df_athletes[
            (gold_medalist | silver_medalist | bronze_medalist)
            & summer_games
            & filter_female
        ]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="female_avg_age")
    )

    female_medalist_winter_avg_age = (
        df_athletes[
            (gold_medalist | silver_medalist | bronze_medalist)
            & winter_games
            & filter_female
        ]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="female_avg_age")
    )

    # plotting
    fig, axs = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    # summer games
    axs[0].set_facecolor("black")  # background color
    axs[0].patch.set_alpha(0.1)
    axs[0].plot(
        male_medalist_summer_avg_age["year"],
        male_medalist_summer_avg_age["male_avg_age"],
        color="lawngreen",
        label="Male Average Age",
    )
    axs[0].plot(
        female_medalist_summer_avg_age["year"],
        female_medalist_summer_avg_age["female_avg_age"],
        color="tab:purple",
        label="Female Average Age",
    )
    axs[0].scatter(
        female_medalist_summer_avg_age.loc[
            female_medalist_summer_avg_age["female_avg_age"].idxmax(), "year"
        ],
        female_medalist_summer_avg_age["female_avg_age"].max(),
        marker="o",
        color="tab:red",
        facecolors="none",
    )
    axs[0].set_title("[Summer Games] Male & Female Medalists Average Age")
    axs[0].set_ylabel("Average Age")
    axs[0].set_ylim
    axs[0].legend()
    axs[0].grid(True)
    # Winter
    axs[1].set_facecolor("blue")  # background color
    axs[1].patch.set_alpha(0.1)
    axs[1].plot(
        male_medalist_winter_avg_age["year"],
        male_medalist_winter_avg_age["male_avg_age"],
        color="lawngreen",
        label="Male Average Age",
    )
    axs[1].plot(
        female_medalist_winter_avg_age["year"],
        female_medalist_winter_avg_age["female_avg_age"],
        color="tab:purple",
        label="Female Average Age",
    )
    axs[1].set_title("[Winter Games] Male & Female Medalists Average Age")
    axs[1].set_ylabel("Average Age")
    axs[1].set_xlabel("Year")
    axs[1].set_ylim
    axs[1].legend()
    axs[1].grid(True)

    print(
        female_medalist_summer_avg_age.loc[
            female_medalist_summer_avg_age["female_avg_age"].idxmax(), "year"
        ]
    )

    # -------------------------------------#
    # ---------- Male and Female ----------#
    # -------------------------------------#

    # Creating the df´s for all participants in a specific game and calculating the average age
    male_avg_age = (
        df_athletes[filter_male]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="male_avg_age")
    )
    female_avg_age = (
        df_athletes[filter_female]
        .groupby("year")["age"]
        .mean()
        .reset_index(name="female_avg_age")
    )
    # plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_facecolor("green")  # background color
    ax.patch.set_alpha(0.1)
    # data
    ax.plot(
        male_avg_age["year"],
        male_avg_age["male_avg_age"],
        label="Male",
        color="lawngreen",
    )
    ax.plot(
        female_avg_age["year"],
        female_avg_age["female_avg_age"],
        label="Female",
        color="tab:purple",
    )
    # labeling
    ax.set_title(
        "[Summer & Winter Olympics] Average Age of Male and Female Athletes Over Time",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Average Age", fontsize=12)
    ax.legend()
    ax.grid(True)

    # Show Plot
    plt.tight_layout()
    plt.show()

    return df_athletes


def get_gender_ratio_change(conn, include_dns=True):
    """
    This function queries the count of athletes who participated in each year, and also queries the
    gender count.

    Args:
    - conn: Database connection object.
    - include_dns: Whether to include athletes with DNS (DID NOT START).
    """

    if include_dns:
        query = """
        SELECT game.year, game.title, 
        COUNT(DISTINCT athlete.athlete_id) AS total_participants,
        COUNT(DISTINCT athlete.athlete_id) FILTER (WHERE athlete.gender = 'Male') AS male_participants,
        COUNT(DISTINCT athlete.athlete_id) FILTER (WHERE athlete.gender = 'Female') AS female_participants
        FROM result
        INNER JOIN athlete ON result.athlete_id = athlete.athlete_id
        INNER JOIN game ON result.game_id = game.game_id
        GROUP BY game.year, game.title;
        """
    else:
        query = """
        SELECT game.year, game.title, 
        COUNT(DISTINCT athlete.athlete_id) AS total_participants,
        COUNT(DISTINCT athlete.athlete_id) FILTER (WHERE athlete.gender = 'Male') AS male_participants,
        COUNT(DISTINCT athlete.athlete_id) FILTER (WHERE athlete.gender = 'Female') AS female_participants
        FROM result
        INNER JOIN athlete ON result.athlete_id = athlete.athlete_id
        INNER JOIN game ON result.game_id = game.game_id
        WHERE NOT result.position IN ('DNS')
        GROUP BY game.year, game.title;
        """

    # creating a pandas DataFrame with the above query
    df_count = pd.read_sql_query(query, conn)

    # creating new columns in the df, for plotting the percent (gender ratio) given total participants for
    # specific games/year
    df_count["male_in_percent"] = (
        df_count["male_participants"] / df_count["total_participants"]
    )
    df_count["female_in_percent"] = (
        df_count["female_participants"] / df_count["total_participants"]
    )
    df_count["game_season"] = df_count["title"].str.extract(r"(Summer|Winter)")

    # extracting Summer / Winter
    df_count_summer = df_count[df_count["game_season"] == "Summer"]
    df_count_winter = df_count[df_count["game_season"] == "Winter"]

    # plot:
    fig, axs = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # summer games figure
    axs[0].set_facecolor("black")  # background color
    axs[0].patch.set_alpha(0.1)
    axs[0].bar(
        df_count_summer["year"],
        df_count_summer["male_in_percent"] * 100,
        label="Male",
        color="lawngreen",
    )
    axs[0].bar(
        df_count_summer["year"],
        df_count_summer["female_in_percent"] * 100,
        bottom=df_count_summer["male_in_percent"] * 100,
        label="Female",
        color="tab:purple",
    )
    axs[0].set_title("[Summer Games] Male vs. Female Participants in Percent")
    axs[0].set_xlabel("Year")
    axs[0].set_ylabel("Percent [%]")
    axs[0].legend()

    # winter games figure
    axs[1].set_facecolor("blue")  # background color
    axs[1].patch.set_alpha(0.1)
    axs[1].bar(
        df_count_winter["year"],
        df_count_winter["male_in_percent"] * 100,
        label="Male",
        color="lawngreen",
    )
    axs[1].bar(
        df_count_winter["year"],
        df_count_winter["female_in_percent"] * 100,
        bottom=df_count_winter["male_in_percent"] * 100,
        label="Female",
        color="tab:purple",
    )
    axs[1].set_title("[Winter Games] Male vs. Female Participants in Percent")
    axs[1].set_xlabel("Year")
    axs[1].set_ylabel("Percent [%]")
    axs[1].legend()

    plt.tight_layout()
    plt.show()


# --------------------------------#
# ---------- Functions ----------#
# --------------------------------#


def get_results_table(conn):
    cur = conn.cursor()

    cur.execute("Select * FROM result WHERE result.position IN ('1', '2', '3')")
    results = cur.fetchall()

    # Creating a df object and formating the column headers
    df_results = pd.DataFrame(results)
    colnames = [d[0] for d in cur.description]
    df_results.columns = colnames
    df_results.set_index("result_id", inplace=True)

    cur.close()
    return df_results


def get_athlete_table(conn):
    cur = conn.cursor()

    cur.execute("Select athlete_id, gender, name, country_id FROM athlete")
    athletes = cur.fetchall()

    # Creating a df object and formating the column headers
    df_athletes = pd.DataFrame(athletes)
    colnames = [d[0] for d in cur.description]
    df_athletes.columns = colnames
    df_athletes.set_index("athlete_id", inplace=True)

    cur.close()
    return df_athletes


def get_game_table(conn):
    cur = conn.cursor()

    cur.execute("Select * FROM game WHERE was_held IS true")
    game = cur.fetchall()

    # Creating a df object and formating the column headers
    df_games = pd.DataFrame(game)
    colnames = [d[0] for d in cur.description]
    df_games.columns = colnames
    df_games.set_index("game_id", inplace=True)

    cur.close()
    return df_games


def get_country_table(conn):
    cur = conn.cursor()

    cur.execute("Select * FROM country")
    country = cur.fetchall()

    # Creating a df object and formating the column headers
    df_countries = pd.DataFrame(country)
    colnames = [d[0] for d in cur.description]
    df_countries.columns = colnames
    df_countries.set_index("country_id", inplace=True)

    cur.close()
    return df_countries


def get_event_table(conn):
    cur = conn.cursor()

    cur.execute("Select * FROM event")
    event = cur.fetchall()

    # Creating a df object and formating the column headers
    df_event = pd.DataFrame(event)
    colnames = [d[0] for d in cur.description]
    df_event.columns = colnames
    df_event.set_index("event_id", inplace=True)

    cur.close()
    return df_event


def get_sport_table(conn):
    cur = conn.cursor()

    cur.execute("Select * FROM sport")
    sport = cur.fetchall()

    # Creating a df object and formating the column headers
    df_sport = pd.DataFrame(sport)
    colnames = [d[0] for d in cur.description]
    df_sport.columns = colnames
    df_sport.set_index("sport_id", inplace=True)

    cur.close()
    return df_sport


"""
# - Change in Olympic Success Over Time by Country / Summer and Winter 
def get_change_of_success_over_time_by_country(conn):
    # get my cursor for creating objects
    cur = conn.cursor()
    
    cur.execute("Select * FROM result WHERE result.position IN ('1', '2', '3')")
    results = cur.fetchall()
    print(len(results))

    cur.close()

# - Relationship Between Success and Athlete Count Per Country Over Time
def get_relationship_between_success_and_athlete_count_per_country(conn):
    pass

# - Impact of Gender Ratio on Success
def get_impact_of_gender_ratio_on_success(conn):
    pass

# - Average Age of Athletes vs. Medal Success
def get_average_age_of_athletes_vs_medal_success(conn):
    pass

# - Host Country Advantage in Medal Count
def host_country_advantage_in_medal_count(conn):
    pass

# maybe athletes participating per country to medals won ratio
"""


# main function
def main():
    # db params
    db_config_params = DBConfig()

    # connect to db
    conn = connect_to_db(db_config_params)

    # creating dataframe from db and plotting
    df_athletes_ages = get_table_with_calculated_age(conn=conn)
    # print(df_athletes_ages.head())

    get_gender_ratio_change(conn=conn, include_dns=True)
    conn.close()


if __name__ == "__main__":

    main()
