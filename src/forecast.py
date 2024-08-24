# forecast.py
import polars as pl
from datetime import date
from preparation.roster import get_roster
from preparation.months import generate_month_ranges

# TODO Replace with input prompts
START_DATE = date(year=2024, month=1, day=22)
END_DATE = date(year=2028, month=12, day=7)
INFLATION_RATE = 0.03
INFLATION_START = date(year=2025, month=1, day=1)
INFLATION_FREQUENCY_IN_MONTHS = 12
ROSTER_PATH = "../data/Personnel forecast - Personnel List.csv"


def add_year_column(base):
    return base.with_columns(pl.col("start_of_month").dt.year().alias("year"))


def add_proration(base):
    return base.with_columns(
        # Get number of active days
        proration=pl.max_horizontal(
            # Earlier of end date or end of month
            pl.min_horizontal("end_of_month", "end_date_complete").sub(
                # Subtract l                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ater of start date or beginning of month
                pl.max_horizontal("start_of_month", "start_date_complete")
                # Reduce by 1 so that start day will be counted in active total
                - pl.duration(days=1)
            ),
            # Make sure at least 0 to cover the case where end date is less than start
            pl.duration(days=0),
        )
        # Convert days to integer (24 hrs/day 60 min/hr 60 sec/min 1000 ms/sec)
        .cast(pl.Float64)
        // (24 * 60 * 60 * 1_000)
        # Divide by total days in month
        / pl.col("end_of_month").dt.day()
    )


def add_headcount_column(base):
    return base.with_columns(
        pl.when(
            (pl.col("start_date_complete") <= pl.col("end_of_month"))
            & (pl.col("end_date_complete") > pl.col("end_of_month"))
        )
        .then(pl.lit(1))
        .otherwise(pl.lit(0))
        .alias("headcount")
    )


def add_headcount_change_column(base):
    return base.with_columns(
        (
            # Calculate starts
            pl.when(
                (pl.col("start_date_complete") <= pl.col("end_of_month"))
                & (pl.col("start_date_complete") >= pl.col("start_of_month"))
            )
            .then(pl.lit(1))
            .otherwise(pl.lit(0))
            +
            # Calculate ends
            pl.when(
                (pl.col("end_date_complete") <= pl.col("end_of_month"))
                & (pl.col("end_date_complete") >= pl.col("start_of_month"))
            )
            .then(pl.lit(-1))
            .otherwise(pl.lit(0))
        ).alias("headcount_change")
    )


def calculate_compensation(base):
    # Calculate monthly salary, bonus, and commission
    base = base.with_columns(
        (
            pl.col("Salary") * pl.col("proration") * pl.col("inflation_factor") / 12
        ).alias("salary_amount"),
        (
            pl.col("Salary")
            * pl.col("Bonus")
            * pl.col("proration")
            * pl.col("inflation_factor")
            / 12
        ).alias("bonus_amount"),
        (
            pl.col("Salary")
            * pl.col("Commission")
            * pl.col("proration")
            * pl.col("inflation_factor")
            / 12
        ).alias("commission_amount"),
    )
    # Calculate total compensation
    base = base.with_columns(
        (
            pl.col("salary_amount")
            + pl.col("bonus_amount")
            + pl.col("commission_amount")
        ).alias("compensation"),
    )

    return base


def calculate_ytd_compensation(base):
    return base.sort(["Employee ID", "year", "start_of_month"]).with_columns(
        pl.col("compensation")
        .cum_sum()
        .over(["Employee ID", "year"])
        .alias("ytd_compensation")
    )


def filter_active_months(base):
    return base.filter(
        (pl.col("start_date_complete") <= pl.col("end_of_month"))
        & (pl.col("end_date_complete") >= pl.col("start_of_month"))
    )


def generate_forecast_base(start_date, end_date, infl_rate, infl_start, infl_freq):
    """
    Generate a base forecast with rows for all employees in roster and active months in range with compensation and headcount data.

    Inputs
    start_date: start date of forecast range,
    end_date: end date of forecast range,
    infl_rate: inflation rate,
    infl_start: start date for inflation increases,
    infl_freq: number of months between inflation frequency

    Output
    Polars dataframe
    """
    # Generate the month ranges
    month_ranges = generate_month_ranges(
        start_date,
        end_date,
        infl_rate,
        infl_start,
        infl_freq,
    )

    # Create a DataFrame from the month ranges
    forecast_base = pl.DataFrame(
        month_ranges,
        schema=["start_of_month", "end_of_month", "inflation_factor"],
        orient="row",
    )

    # Create a roster from input file
    roster = get_roster(ROSTER_PATH)

    # Cross join to roster
    forecast_base = forecast_base.join(roster, how="cross")

    # Apply transformations
    forecast_base = filter_active_months(forecast_base)
    forecast_base = add_year_column(forecast_base)
    forecast_base = add_proration(forecast_base)
    forecast_base = add_headcount_column(forecast_base)
    forecast_base = add_headcount_change_column(forecast_base)
    forecast_base = calculate_compensation(forecast_base)
    forecast_base = calculate_ytd_compensation(forecast_base)

    return forecast_base


def rate_forecast(forecast, base_column, new_column_name, applied_rate):
    """
    Add a new column to a forecast that is an amount calculated as a percentage of an existing column

    Inputs
    forecast: dataframe - current forecast
    base_column: str - column to calculate % of
    new_column_name: str - name of new column
    applied_rate: float - percentage rate to apply

    Output
    dataframe with new column added
    """

    # Check if the base_column exists in the forecast
    if base_column not in forecast.columns:
        print(f"Column '{base_column}' not found in forecast. Cannot apply rate.")

    # Check if the base_column is of a numeric type
    elif not forecast[base_column].dtype.is_numeric():
        print(f"Column '{base_column}' is not a numeric type. Cannot apply rate.")
        return forecast

    # Add the new column as a percentage of the base_column
    else:
        forecast = forecast.with_columns(
            (pl.col(base_column) * applied_rate).alias(new_column_name)
        )

    return forecast


def capped_rate_forecast(
    forecast, base_column, new_column_name, applied_rate, cap_base_column, cap_amount
):
    """
    Add a new column to a forecast that is an amount calculated as a percentage of an existing column,
    with a cap on the base amount.

    Inputs
    forecast: dataframe - current forecast
    base_column: str - column to calculate % of
    new_column_name: str - name of new column
    applied_rate: float - percentage rate to apply
    cap_base_column: str - column used to determine the whether cap has been exceeded
    cap_amount: float - maximum amount of cap_base_column to apply the rate to

    Output
    DataFrame with the new column added.
    """

    # Ensure base_column and cap_base_column exist and are numeric
    if base_column not in forecast.columns or cap_base_column not in forecast.columns:
        raise ValueError(
            f"Forecast could not be applied: column '{base_column}' or '{cap_base_column}' not found."
        )

    if (
        not forecast[base_column].dtype.is_numeric()
        or not forecast[cap_base_column].dtype.is_numeric()
    ):
        raise ValueError(
            f"Forecast could not be applied: column '{base_column}' or '{cap_base_column}' is not numeric."
        )

    # Compute the capped rate
    capped_rate_expr = pl.when(pl.col(cap_base_column) <= cap_amount)
    capped_rate_expr = capped_rate_expr.then(pl.col(base_column) * applied_rate)
    capped_rate_expr = capped_rate_expr.when(
        pl.col(cap_base_column) - pl.col(base_column) >= cap_amount
    )
    capped_rate_expr = capped_rate_expr.then(pl.lit(0))
    capped_rate_expr = capped_rate_expr.otherwise(
        (cap_amount - pl.col(cap_base_column) + pl.col(base_column)).clip(lower_bound=0)
        * applied_rate
    ).alias(new_column_name)

    return forecast.with_columns(capped_rate_expr)

def per_head_forecast(
    forecast, new_column_name, amount
):
    """
    Add a new column to a forecast that is a flat amount adjusted for inflation for any month an employee is active

    Inputs
    forecast: dataframe - current forecast
    new_column_name: str - name of new column
    amount: number - monthly amount of expense

    Output
    DataFrame with the new column added.
    """

    # Ensure that proration and inflation_factor columns exist and are numeric
    if (
        "proration" not in forecast.columns
        or "inflation_factor" not in forecast.columns
        or not forecast["proration"].dtype.is_numeric()
        or not forecast["inflation_factor"].dtype.is_numeric()
    ):
        raise ValueError("Forecast could not be applied: column 'proration' or 'inflation_factor' not found or not numeric.")
    
    # Find the maximum proration per Employee ID and start_of_month
    max_prorations = forecast.group_by(["Employee ID", "start_of_month"]).agg(
        pl.col("proration").max().alias("max_proration")
    )

    # Join back to the original forecast to identify rows with the maximum proration
    forecast = forecast.join(max_prorations, on=["Employee ID", "start_of_month"])

    # Apply the amount only to the rows with the maximum proration to avoid duplication when an employee changes roles mid month
    forecast = forecast.with_columns(
        pl.when((pl.col("proration") == pl.col("max_proration")) & (pl.col("proration") > 0))
        .then(pl.col("inflation_factor") * amount)
        .otherwise(0)
        .alias(new_column_name)
    )

    # Drop the temporary max_proration column
    forecast = forecast.drop("max_proration")

    return forecast


if __name__ == "__main__":
    forecast = generate_forecast_base(
        START_DATE,
        END_DATE,
        INFLATION_RATE,
        INFLATION_START,
        INFLATION_FREQUENCY_IN_MONTHS,
    )

    forecast = rate_forecast(forecast, "compensation", "retirement", 0.03)
    forecast = capped_rate_forecast(
        forecast=forecast,
        base_column="compensation",
        new_column_name="ss_tax",
        applied_rate=0.062,
        cap_base_column="ytd_compensation",
        cap_amount=168600,
    )
    forecast = per_head_forecast(
        forecast=forecast, 
        new_column_name="health_insurance",
        amount=500
    )

    # with pl.Config(tbl_cols=-1):
    # print(forecast_base)
    # print(forecast_base.filter(pl.col("proration") < 1).filter(pl.col("proration") > 0))
    # print(forecast_base.filter(pl.col("Role ID") < 3))

    forecast.write_csv(file="./forecast.csv")
