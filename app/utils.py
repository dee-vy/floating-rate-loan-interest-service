import os
import sqlite3
from datetime import date, datetime, timedelta
from io import BytesIO

import pandas as pd
import requests


def fetch_excel():
    """
    Tries to fetch today’s forward rates Excel file. Retries up to 3 times.
    Falls back to yesterday’s file if today’s isn’t available.
    :return: Tuple of BytesIO Excel data and a boolean indicating if it's current day's data.
    """
    today = date.today()
    for i in range(0, 3):
        try:
            return excel_retrieval(today), True
        except requests.exceptions.RequestException:
            print(f"Today's Forward Rates sheet not found. Retry attempt({i + 1})")

    print("\nIt seems that today's Forward Rates sheet isn't up yet, so the service will fallback to yesterday's file.")
    yesterday = datetime.today() - timedelta(1)
    return excel_retrieval(yesterday), False


def excel_retrieval(given_date):
    """
    Downloads the forward curve Excel file for a given date.
    :param given_date: Date to format and use in the download URL.
    :return: BytesIO of the Excel file.
    """
    given_date = given_date.strftime("%m.%d.%Y")
    url = f"https://19621209.fs1.hubspotusercontent-na1.net/hubfs/19621209/Forward%20Curves/Pensford" \
          f"%20Forward%20Curve%20-%2{given_date}.xlsx"
    response = requests.get(url)
    response.raise_for_status()
    return BytesIO(response.content)


def parse_excel(xls):
    """
    Parses the Excel file and returns a cleaned DataFrame with reset dates and rates.
    :param xls: BytesIO Excel file.
    :return: DataFrame with 'date' and 'rate' columns.
    """
    df = pd.read_excel(xls, sheet_name="Forward Curve", skiprows=4)
    df = df.iloc[:, [6, 7]]
    df.columns = ["date", "rate"]
    df.dropna(subset=["date", "rate"], how="any", inplace=True)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    print(f"First five rows: \n{df.head()}")
    print(df.shape)
    return df


def store(df, is_current_day_rates):
    """
    Stores forward rates in SQLite DB only if latest data isn’t already saved.
    :param df: DataFrame to store.
    :param is_current_day_rates: Flag indicating if the df is from today.
    :return:
    """
    db_file_path = get_db_path()
    if os.path.isfile(db_file_path):
        conn = sqlite3.connect(db_file_path)
        earliest_stored_date = conn.execute("select min(date) from forward_rates").fetchone()[0]
        earliest_stored_date = datetime.strptime(earliest_stored_date, "%Y-%m-%d").date()
        if earliest_stored_date == date.today():
            print("Forward rates already stored today!")
            conn.close()
            return
        elif (earliest_stored_date == date.today() - timedelta(days=1)) and not is_current_day_rates:
            print("Yesterday’s forward rates already stored.")
            conn.close()
            return
        df.to_sql("forward_rates", conn, if_exists="replace", index_label=False)
        conn.close()
        return
    else:
        conn = sqlite3.connect(db_file_path)
        df.to_sql("forward_rates", conn, if_exists="replace", index_label=False)
        conn.close()


def get_db_path():
    """
    Returns absolute path to the forward_rates.db file inside the /data directory.
    :return: String path to the SQLite DB file.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_file_path = os.path.join(base_dir, "..", "data", "forward_rates.db")
    db_file_path = os.path.abspath(db_file_path)
    return db_file_path
