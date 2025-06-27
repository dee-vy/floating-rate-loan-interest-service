from unittest.mock import patch

import pandas as pd
from fastapi.testclient import TestClient

from app.controller import app

client = TestClient(app)


class TestController:

    @patch("app.controller.store")
    @patch("app.controller.get_final_rate")
    @patch("app.controller.parse_excel")
    @patch("app.controller.fetch_excel")
    def test_valid_input_return_200(self, mock_fetch, mock_parse, mock_get_rate, mock_store):
        mock_fetch.return_value = ("dummy_excel", True)
        mock_parse.return_value = pd.DataFrame([{"date": "2025-06-25", "rate": 0.05}])
        mock_get_rate.return_value = [{"date": "2025-06-25", "rate": 0.07}]
        payload = {
            "maturity_date": "2025-06-25",
            "reference_rate": "SOFR",
            "rate_floor": 0.02,
            "rate_ceiling": 0.10,
            "rate_spread": 0.02
        }
        response = client.post("/loan-rate-curve/", json=payload)
        assert response.status_code == 200
        assert response.json() == [{"date": "2025-06-25", "rate": 0.07}]
        assert isinstance(response.json(), list)
        assert all("date" in r and "rate" in r for r in response.json())

    def test_invalid_input_return_422(self):
        payload = {
            "maturity_date": "2025/08/01",
            "reference_rate": "SOFR",
            "rate_floor": 0.02,
            "rate_ceiling": 0.10,
            "rate_spread": "even"
        }

        response = client.post("/loan-rate-curve/", json=payload)
        assert response.status_code == 422
