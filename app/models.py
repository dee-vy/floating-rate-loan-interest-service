from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class RequestPayload(BaseModel):
    """
    Input payload for the interest rate calculation endpoint.

    Fields:
    - maturity_date: End date for the loan.
    - rate_floor: Minimum allowed interest rate.
    - rate_ceiling: Maximum allowed interest rate.
    - rate_spread: Spread to be added on top of the reference rate of each month.
    """
    maturity_date: date
    rate_floor: Decimal
    rate_ceiling: Decimal
    rate_spread: Decimal


class Rate(BaseModel):
    """
    Output representing each month's interest rate up to the maturity date.

    Fields:
    - date: The month corresponding to the rate.
    - rate: The final interest rate for that month.
    """
    date: date
    rate: float
