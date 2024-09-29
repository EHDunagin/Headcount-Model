# base.py
import polars as pl
from forecast.utilities import get_roster, generate_month_ranges


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


def generate_forecast_base(
    roster_path, start_date, end_date, infl_rate, infl_start, infl_freq
):
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
    roster = get_roster(roster_path)

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


# if __name__ == "__main__":

#     # Get user input for each variable
#     START_DATE = datetime.strptime(input("Enter the start date (YYYY-MM-DD): "), "%Y-%m-%d").date()
#     END_DATE = datetime.strptime(input("Enter the end date (YYYY-MM-DD): "), "%Y-%m-%d").date()
#     INFLATION_RATE = float(input("Enter the inflation rate (e.g., 0.03 for 3%): "))
#     INFLATION_START = datetime.strptime(input("Enter the inflation start date (YYYY-MM-DD): "), "%Y-%m-%d").date()
#     INFLATION_FREQUENCY_IN_MONTHS = int(input("Enter the inflation frequency in months: "))

#     # Open a file dialog to select the roster CSV file
#     from tkinter.filedialog import askopenfilename
#     ROSTER_PATH = askopenfilename(title="Select the roster CSV file", filetypes=[("CSV files", "*.csv")])

#     forecast = generate_forecast_base(
#         ROSTER_PATH,
#         START_DATE,
#         END_DATE,
#         INFLATION_RATE,
#         INFLATION_START,
#         INFLATION_FREQUENCY_IN_MONTHS,
#     )

#     forecast.write_csv(file=f"./{datetime.today().strftime('%y-%m-%d')}_forecast.csv")
