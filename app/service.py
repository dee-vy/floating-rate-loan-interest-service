from decimal import Decimal, ROUND_HALF_UP

from app.models import Rate


def get_final_rate(payload, reference_rate):
    """
    Calculates the monthly floating interest rates from today until the given maturity date.

    For each month, adds the spread to the forward rate and ensures the final rate
    stays within the specified floor and ceiling.
    :param payload: User inputs with maturity_date, floor, ceiling, and spread.
    :param reference_rate: DataFrame containing SOFR forward rates for each month.
    :return: List of Rate objects, one per month, from today to maturity_date.
    """
    final_rate = []
    for _, row in reference_rate.iterrows():
        date = row["date"]
        if date <= payload.maturity_date:
            rate = Decimal(str(row["rate"])) + payload.rate_spread
            rate = min(max(rate, payload.rate_floor), payload.rate_ceiling)
            rate = rate.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP)
            final_rate.append(Rate(date=date, rate=float(rate)))
        else:
            break
    print(f"\nMaturity date: {payload.maturity_date}\nFinal rates: \n{final_rate}\n")
    return final_rate
