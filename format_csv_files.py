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

TABLE_TO_CSV = {
    "Athlete": "athlete.csv",
    "Country": "country.csv",
    "Event": "event.csv",
    "Game": "game.csv",
}

CSV_NAME_MAPPING = {
    "Olympic_Athlete_Bio.csv": TABLE_TO_CSV["Athlete"],
    "Olympics_Country.csv": TABLE_TO_CSV["Country"],
    "Olympic_Athlete_Event_Results.csv": TABLE_TO_CSV["Event"],
    "Olympics_Games.csv": TABLE_TO_CSV["Game"],
}

# ---------------------------
# ---------- UTILS ----------
# ---------------------------


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted: {os.path.basename(file_path)}")
    else:
        print(f"Error: File {file_path} does not exist.")


def delete_directory(directory_path):
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


def rename_file(old_path, new_path):
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f"Renamed: {os.path.basename(old_path)} -> {os.path.basename(new_path)}")
    else:
        print(f"File not found: {old_path}")


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
# ---------- TABLE COMBINATION -------
# ------------------------------------



# ------------------------------------
# ---------- CSV FORMATTING ----------
# ------------------------------------


def format_countries():
    path = os.path.join(DATASET_PATH, TABLE_TO_CSV["Country"])
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
    path = os.path.join(DATASET_PATH, TABLE_TO_CSV["Athlete"])
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
    path = os.path.join(DATASET_PATH, TABLE_TO_CSV["Game"])
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

    delete_columns(df, ["edition_url", "year", "country_flag_url", "competition_date"])

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
    columns = ["game_id"] + [col for col in df.columns if col not in ["game_id", "country_id"]] + ["country_id"]
    df = df[columns]

    # Turns "is_held" into a boolean
    df["was_held"] = ~df["was_held"].notna() & df["was_held"].astype(str).str.strip().ne("")

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

    # TABLE COMBINATION

    # CSV FORMATTING
    format_countries()
    format_athletes()
    format_games()


if __name__ == "__main__":
    main()
