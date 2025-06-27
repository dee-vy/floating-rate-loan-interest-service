from datetime import date, timedelta
from io import BytesIO
from unittest.mock import patch, MagicMock

import pandas as pd
import requests

from app.utils import parse_excel, fetch_excel
from app.utils import store


class TestUtils:

    @patch("app.utils.excel_retrieval")
    def test_fallback_to_yesterday(self, mock_excel_retrieval):
        mock_excel_retrieval.side_effect = [requests.exceptions.RequestException()] * 3 + [("dummy_data")]

        result = fetch_excel()
        assert result[1] is False
        assert mock_excel_retrieval.call_count == 4

    def test_parse_excel_removes_nan_rows(self):
        df_with_nans = pd.DataFrame({
            "A": [None, None],
            "B": [None, None],
            "C": [None, None],
            "D": [None, None],
            "E": [None, None],
            "F": [None, None],
            "Unnamed: 6": [pd.Timestamp("2025-06-25"), None],
            "Unnamed: 7": [0.05, None]
        })
        buffer = BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            df_with_nans.to_excel(writer, index=False, sheet_name="Forward Curve", startrow=4)
        buffer.seek(0)

        result_df = parse_excel(buffer)
        assert len(result_df) == 1
        assert not result_df.isnull().values.any()

    def test_parse_excel_output_format(self):
        df = pd.DataFrame({
            "A": [None],
            "B": [None],
            "C": [None],
            "D": [None],
            "E": [None],
            "F": [None],
            "Unnamed: 6": [pd.Timestamp("2025-06-25")],
            "Unnamed: 7": [0.05]
        })
        buffer = BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            df.to_excel(writer, index=False, sheet_name="Forward Curve", startrow=4)
        buffer.seek(0)

        result_df = parse_excel(buffer)
        assert "date" in result_df.columns
        assert "rate" in result_df.columns
        assert isinstance(result_df["date"].iloc[0], date)
        assert isinstance(result_df["rate"].iloc[0], float)
        assert result_df.iloc[0]["date"] == date(2025, 6, 25)
        assert result_df.iloc[0]["rate"] == 0.05

    @patch("app.utils.os.path.isfile")
    @patch("app.utils.sqlite3.connect")
    @patch("app.utils.get_db_path")
    def test_store_skips_if_today_already_stored(self, mock_get_path, mock_connect, mock_isfile):
        mock_get_path.return_value = "dummy_path"
        mock_isfile.return_value = True
        mock_conn = MagicMock()
        mock_cursor = mock_conn.execute.return_value
        mock_cursor.fetchone.return_value = [date.today().strftime("%Y-%m-%d")]
        mock_connect.return_value = mock_conn

        dummy_df = pd.DataFrame({"date": [date.today()], "rate": [0.05]})
        store(dummy_df, is_current_day_rates=True)

        mock_conn.execute.assert_called_with("select min(date) from forward_rates")
        mock_conn.close.assert_called_once()
        mock_conn.to_sql.assert_not_called()

    @patch("app.utils.os.path.isfile")
    @patch("app.utils.sqlite3.connect")
    @patch("app.utils.get_db_path")
    def test_store_skips_if_yesterday_already_stored(self, mock_get_path, mock_connect, mock_isfile):
        mock_get_path.return_value = "dummy_path"
        mock_isfile.return_value = True
        mock_conn = MagicMock()
        mock_cursor = mock_conn.execute.return_value
        mock_cursor.fetchone.return_value = [(date.today() - timedelta(days=1)).strftime("%Y-%m-%d")]
        mock_connect.return_value = mock_conn

        dummy_df = pd.DataFrame({"date": [date.today() - timedelta(days=1)], "rate": [0.05]})
        store(dummy_df, is_current_day_rates=False)

        mock_conn.execute.assert_called_once()
        mock_conn.close.assert_called_once()
        mock_conn.to_sql.assert_not_called()

    @patch("app.utils.pd.DataFrame.to_sql")
    @patch("app.utils.sqlite3.connect")
    @patch("app.utils.get_db_path")
    @patch("app.utils.os.path.isfile")
    def test_store_creates_db_if_not_exists(self, mock_isfile, mock_get_path, mock_connect, mock_to_sql):
        mock_get_path.return_value = "dummy_path"
        mock_isfile.return_value = False
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        dummy_df = pd.DataFrame({"date": [date.today()], "rate": [0.05]})
        store(dummy_df, is_current_day_rates=True)

        mock_to_sql.assert_called_once()
        mock_conn.close.assert_called_once()
