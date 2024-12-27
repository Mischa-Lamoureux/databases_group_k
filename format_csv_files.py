import os
import re
import shutil
import kagglehub
import pandas as pd
from typing import List

# ----------------------------
# ---------- CONFIG ----------
# ----------------------------

DATASET_URL = "josephcheng123456/olympic-historical-dataset-from-olympediaorg"

BASE_DIRECTORY = "./"
DATASET_FOLDER = "dataset"
DATASET_PATH = f"{BASE_DIRECTORY}{DATASET_FOLDER}"

IRRELEVANT_FILES = ["Olympic_Games_Medal_Tally.csv", "Olympic_Results.csv"]

CSV_NAMES = {
    "Athlete": "athlete.csv",
    "Country": "country.csv",
    "Event": "event.csv",
    "Game": "game.csv",
    "Sport": "sport.csv",
    "Result": "result.csv",
}

CSV_NAME_MAPPING = {
    "Olympic_Athlete_Bio.csv": CSV_NAMES["Athlete"],
    "Olympics_Country.csv": CSV_NAMES["Country"],
    "Olympic_Athlete_Event_Results.csv": CSV_NAMES["Event"],
    "Olympics_Games.csv": CSV_NAMES["Game"],
}

# ---------------------------
# ---------- UTILS ----------
# ---------------------------


def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted: {os.path.basename(file_path)}")
    else:
        print(f"Error: File {file_path} does not exist.")


def delete_directory(directory_path: str):
    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")

    try:
        if os.path.isdir(directory_path):
            shutil.rmtree(directory_path)
            print(
                f"Directory '{directory_path}' and all its contents have been deleted."
            )
        else:
            print(f"Error: '{directory_path}' is not a directory.")
    except Exception as e:
        print(f"Error while deleting directory '{directory_path}': {str(e)}")


def rename_file(old_path: str, new_path: str):
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f"Renamed: {os.path.basename(old_path)} -> {os.path.basename(new_path)}")
    else:
        print(f"File not found: {old_path}")


def duplicate_file(source_path: str, target_path: str):
    try:
        shutil.copyfile(source_path, target_path)
        print(f"File duplicated successfully from '{source_path}' to '{target_path}'.")
    except FileNotFoundError:
        print(f"Error: Source file '{source_path}' does not exist.")
    except Exception as e:
        print(f"Error: Could not duplicate the file. {str(e)}")


def move_folder(source_folder: str, dest_folder: str, folder_name: str = None):
    if not os.path.exists(source_folder):
        return f"Error: Source folder '{source_folder}' does not exist."

    os.makedirs(dest_folder, exist_ok=True)

    if folder_name is None:
        folder_name = os.path.basename(source_folder)

    target_path = os.path.join(dest_folder, folder_name)

    try:
        shutil.move(source_folder, target_path)
        return f"Folder successfully moved to: {target_path}"
    except Exception as e:
        return f"Error while moving folder: {str(e)}"


def delete_columns(df: pd.DataFrame, column_names: List[str]):
    for column_name in column_names:
        if column_name in df.columns:
            df.drop(columns=[column_name], inplace=True)
            print(f"Column '{column_name}' has been deleted.")
        else:
            print(f"Error: Column '{column_name}' does not exist in the DataFrame.")


def rename_columns(df: pd.DataFrame, rename_mapping: dict):
    invalid_columns = [col for col in rename_mapping.keys() if col not in df.columns]

    if invalid_columns:
        print(
            f"Error: The following columns do not exist in the DataFrame: {invalid_columns}"
        )
        return

    df.rename(columns=rename_mapping, inplace=True)
    print(f"Columns have been renamed: {rename_mapping}")


def download_dataset():
    return kagglehub.dataset_download(DATASET_URL)


# ------------------------------------
# ---------- CSV FORMATTING ----------
# ------------------------------------


def format_countries():
    path = os.path.join(DATASET_PATH, CSV_NAMES["Country"])
    df = pd.read_csv(path)

    rename_columns(
        df,
        {
            "noc": "country_id",
            "country": "name",
        },
    )

    # Delete duplicate key for "Russian Olympic Committee"
    df = df[df["name"] != "ROC"]

    df.to_csv(path, index=False)


def format_athletes():
    path = os.path.join(DATASET_PATH, CSV_NAMES["Athlete"])
    df = pd.read_csv(path)

    # Format dates
    df["born"] = df["born"] = pd.to_datetime(df["born"], errors="coerce", dayfirst=True)

    # Delete unnecessary columns
    delete_columns(df, ["country", "description", "special_notes"])

    # Rename columns
    rename_columns(
        df,
        {
            "sex": "gender",
            "born": "date_of_birth",
            "country_noc": "country_id",
        },
    )

    # Clean and fix the weight column
    def clean_weight(value):
        if pd.isna(value):
            return None  # Handle NaN
        match = re.search(r"\d+", str(value))  # Extract the first number
        return int(match.group()) if match else None

    # Replace " International Federation Representative  Italy"
    df["country_id"] = df["country_id"].replace("IFR", "ITA")

    df["weight"] = df["weight"].apply(clean_weight)

    df.to_csv(path, index=False)


def format_games():
    path = os.path.join(DATASET_PATH, CSV_NAMES["Game"])
    df = pd.read_csv(path)

    # Strip leading/trailing spaces
    df["start_date"] = df["start_date"].astype(str).str.strip()
    df["end_date"] = df["end_date"].astype(str).str.strip()

    # Combine and convert to datetime
    df["start_date"] = pd.to_datetime(
        df["start_date"] + " " + df["year"].astype(str), errors="coerce", dayfirst=True
    )
    df["end_date"] = pd.to_datetime(
        df["end_date"] + " " + df["year"].astype(str), errors="coerce", dayfirst=True
    )

    delete_columns(df, ["edition_url", "country_flag_url", "competition_date"])

    rename_columns(
        df,
        {
            "edition_id": "game_id",
            "edition": "title",
            "country_noc": "country_id",
            "isHeld": "was_held",
        },
    )

    # Move game_id to first column and country_id to last column
    columns = (
        ["game_id"]
        + [col for col in df.columns if col not in ["game_id", "country_id"]]
        + ["country_id"]
    )
    df = df[columns]

    # Turns "is_held" into a boolean
    df["was_held"] = ~df["was_held"].notna() & df["was_held"].astype(
        str
    ).str.strip().ne("")

    df.to_csv(path, index=False)


def format_results():
    event_path = os.path.join(DATASET_PATH, CSV_NAMES["Event"])
    result_path = os.path.join(DATASET_PATH, CSV_NAMES["Result"])

    duplicate_file(event_path, result_path)
    result_df = pd.read_csv(result_path)

    delete_columns(
        result_df,
        ["edition", "country_noc", "sport", "event", "athlete", "medal", "isTeamSport"],
    )

    rename_columns(
        result_df,
        {
            "edition_id": "game_id",
            "result_id": "event_id",
            "pos": "position",
        },
    )

    # Delete duplicate rows
    result_df.drop_duplicates(subset=None, keep="first", inplace=True)

    # Add result_id column
    result_df.insert(0, "result_id", range(len(result_df)))

    # Move position to second column
    gender_col = result_df.pop("position")
    result_df.insert(1, "position", gender_col)

    # For results with invalid athelete_ids
    def replace_invalid_athelete_ids():
        athlete_path = os.path.join(DATASET_PATH, CSV_NAMES["Athlete"])
        athlete_df = pd.read_csv(athlete_path)

        # Get set of valid athlete ids
        valid_athlete_ids = set(athlete_df["athlete_id"])

        result_df["athlete_id"] = result_df["athlete_id"].apply(
            lambda x: x if x in valid_athlete_ids else pd.NA
        )

    replace_invalid_athelete_ids()

    result_df.to_csv(result_path, index=False)


def format_sports():
    path = os.path.join(DATASET_PATH, CSV_NAMES["Event"])
    df = pd.read_csv(path)

    # Create a unique mapping for sports
    unique_sports = df["sport"].unique()
    sports_mapping = {sport: idx + 1 for idx, sport in enumerate(unique_sports)}

    # Create a DataFrame for the sport mapping
    sports_df = pd.DataFrame(list(sports_mapping.items()), columns=["name", "sport_id"])
    sports_df = sports_df[["sport_id", "name"]].sort_values("sport_id")

    # Save sport mappings to CSV file
    sports_path = os.path.join(DATASET_PATH, CSV_NAMES["Sport"])
    sports_df.to_csv(sports_path, index=False)

    # Replace sport column with corresponding id
    df["sport_id"] = df["sport"].map(sports_mapping)
    df.drop(columns=["sport"], inplace=True)

    columns = [col for col in df.columns if col != "sport_id"] + ["sport_id"]
    df = df[columns]

    df.to_csv(path, index=False)


def format_events():
    path = os.path.join(DATASET_PATH, CSV_NAMES["Event"])
    df = pd.read_csv(path)

    delete_columns(
        df,
        [
            "edition",
            "edition_id",
            "country_noc",
            "athlete",
            "athlete_id",
            "pos",
            "medal",
        ],
    )

    rename_columns(
        df,
        {
            "result_id": "event_id",
            "event": "name",
            "isTeamSport": "is_team_event",
        },
    )

    # Drop all duplicate event_ids
    df.drop_duplicates(subset=["event_id"], keep="first", inplace=True)

    # Move event_id to the first column
    columns = ["event_id"] + [col for col in df.columns if col != "event_id"]
    df = df[columns]

    # Extract gender from `name`
    df["gender"] = df["name"].str.extract(r"(Men|Women|Boys)$").fillna("")

    # Remove gender suffix from `name`
    df["name"] = (
        df["name"].str.replace(r"(Men|Women|Boys)$", "", regex=True).str.strip(", ")
    )

    # Replace "Boys" with "Men"
    df["gender"] = df["gender"].replace({"Boys": "Men"})

    # Move gender to third column
    gender_col = df.pop("gender")
    df.insert(2, "gender", gender_col)

    df.to_csv(path, index=False)


def main():
    delete_directory(DATASET_PATH)
    download_directory = download_dataset()  # Download dataset
    move_folder(
        download_directory, BASE_DIRECTORY, DATASET_FOLDER
    )  # Move dataset to working directory

    # Delete irrelevant files
    for file in IRRELEVANT_FILES:
        file_path = os.path.join(DATASET_PATH, file)
        delete_file(file_path)

    # Rename files
    for old_name, new_name in CSV_NAME_MAPPING.items():
        old_path = os.path.join(DATASET_PATH, old_name)
        new_path = os.path.join(DATASET_PATH, new_name)

        rename_file(old_path, new_path)

    # CSV FORMATTING
    format_countries()
    format_athletes()
    format_games()
    format_results()
    format_sports()
    format_events()


if __name__ == "__main__":

    main()
