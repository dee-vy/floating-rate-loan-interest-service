from typing import List

from fastapi import FastAPI

from app.models import RequestPayload, Rate
from app.service import get_final_rate
from app.utils import fetch_excel, parse_excel, store

app = FastAPI()


@app.post("/loan-rate-curve/", response_model=List[Rate])
async def loan_rate_controller(payload: RequestPayload):
    """
    Endpoint to calculate and return the floating loan interest rate curve.
    :param payload: RequestPayload containing loan parameters like maturity date, spread, floor, and ceiling.
    :return: List[float] - A list of monthly interest rates from today till the maturity date.
    """
    excel_data, is_current_day_rates = fetch_excel()
    forward_rates_df = parse_excel(excel_data)
    store(forward_rates_df, is_current_day_rates)
    return get_final_rate(payload, forward_rates_df)
