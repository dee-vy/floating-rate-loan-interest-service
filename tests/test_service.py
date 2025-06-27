from datetime import date
from decimal import Decimal

import pandas as pd

from app.models import RequestPayload, Rate
from app.service import get_final_rate


class TestService:

    def test_correct_rate_calculation(self):
        payload = RequestPayload(
            maturity_date=date(2025, 8, 30),
            rate_floor=Decimal("0.02"),
            rate_ceiling=Decimal("0.05"),
            rate_spread=Decimal("0.01")
        )
        reference_data = pd.DataFrame([
            {"date": date(2025, 6, 26), "rate": 0.03},
            {"date": date(2025, 7, 26), "rate": 0.01},
            {"date": date(2025, 8, 26), "rate": 0.06},
            {"date": date(2025, 9, 26), "rate": 0.04}
        ])

        expected_rates = [
            Rate(date=date(2025, 6, 26), rate=0.04),
            Rate(date=date(2025, 7, 26), rate=0.02),
            Rate(date=date(2025, 8, 26), rate=0.05)
        ]

        actual_rates = get_final_rate(payload, reference_data)

        assert isinstance(actual_rates, list)
        assert all(isinstance(r, Rate) for r in actual_rates)
        assert all(r.date <= payload.maturity_date for r in actual_rates)
        assert actual_rates == expected_rates
