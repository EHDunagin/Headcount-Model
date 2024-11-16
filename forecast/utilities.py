# utilities.py
import logging

import polars as pl

from polars.exceptions import ColumnNotFoundError, ComputeError
from datetime import date, timedelta
from rich.console import Console
from rich.logging import RichHandler

# Set up Rich Console
console = Console()

# Set up logging with Rich
logging.basicConfig(
    level=logging.INFO, handlers=[RichHandler(console=console, markup=True)]
)
logger = logging.getLogger("utilities")


def increase_date(start_date, months):
    """Increase a date by a given number of months"""
    if start_date.month + (months % 12) > 12:
        new_date = start_date.replace(
            year=start_date.year + (months // 12) + 1,
            month=start_date.month + (months % 12) - 12,
            day=1,
        )
    else:
        new_date = start_date.replace(
            year=start_date.year + (months // 12),
            month=start_date.month + (months % 12),
            day=1,
        )
    return new_date


def generate_month_ranges(
    start_date, end_date, inflation_rate, inflation_date, inflation_frequency
):
    """Creates a series of month ranges with applicable inflation rate

    Positional arguments:
    start_date -- datetime in the first month
    end_date -- datetime in the last month
    inflation_rate -- rate by which inflation increases
    inflation_date -- date when inflation begins
    inflation_frequency -- number of months between inflation incrementation

    Return value:
    List of tuples of (start of month: date, end of month: date, inflation factor: float)

    Starting on in the month of the start date, finds the first and last day of month for
    every month until the month of the end date incrementing inflation if applicable.
    Adds a tuple with start of month, end of month and inflation factor to a list.

    """
    # Initialize the list of month ranges
    month_ranges = []

    # Start with the first month
    current_date = start_date.replace(day=1)

    # Set starting point for inflation factor
    inflation_factor = 1.0

    console.log("Generating month ranges...")

    while current_date <= end_date:
        # Calculate the first day of the next month
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1)

        # Calculate the last day of the current month
        end_of_month = next_month - timedelta(days=1)

        # Increment inflation if necessary
        if current_date >= inflation_date:
            inflation_factor *= 1.0 + inflation_rate
            inflation_date = increase_date(inflation_date, inflation_frequency)

        # Append the month range to the list
        month_ranges.append((current_date, end_of_month, inflation_factor))

        # Log progress
        logger.debug(f"Processed range: {current_date} - {end_of_month}")

        # Move to the next month
        current_date = next_month

    console.log("[green]Month ranges generated successfully![/green]")

    return month_ranges


def get_roster(data_path):
    """
    Reads in an input headcount roster from a .csv file fills missing start and end dates.

    Input -> path to headcount roster input (string)
    Output -> Polars Dataframe of roster
    """
    console.log(f"Reading roster from [blue]{data_path}[/blue]...")
    roster = pl.read_csv(
        data_path,
        try_parse_dates=True,
        columns=[
            "Role ID",
            "Employee ID",
            "Employee Name",
            "Title",
            "Department",
            "Employment type",
            "Location",
            "Start Date",
            "End Date",
            "Salary",
            "Bonus",
            "Commission",
        ],
        schema_overrides={
            "Role ID": pl.Int32,
            "Employee ID": pl.Utf8,
            "Employee Name": pl.Utf8,
            "Title": pl.Utf8,
            "Department": pl.Utf8,
            "Employment type": pl.Utf8,
            "Location": pl.Utf8,
            "Salary": pl.Float64,
            "Bonus": pl.Float64,
            "Commission": pl.Float64,
        },
    )

    # Convert start and end to dates
    roster = roster.with_columns(
        pl.col("Start Date").str.strptime(
            pl.Date, format="%m/%d/%y", strict=False, exact=True
        ),
        pl.col("End Date").str.strptime(
            pl.Date, format="%m/%d/%y", strict=False, exact=True
        ),
    )

    # Set minimal start date
    roster = roster.with_columns(
        pl.col("Start Date").fill_null(date.min).alias("start_date_complete")
    )

    # Set maximal end date
    roster = roster.with_columns(
        pl.col("End Date").fill_null(date.max).alias("end_date_complete")
    )

    return roster
