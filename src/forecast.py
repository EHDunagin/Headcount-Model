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
ROSTER_PATH = '../data/Personnel forecast - Personnel List.csv'

# Generate the month ranges
month_ranges = generate_month_ranges(START_DATE, END_DATE, INFLATION_RATE, INFLATION_START, INFLATION_FREQUENCY_IN_MONTHS)

# Create a DataFrame from the month ranges
forecast_base = pl.DataFrame(month_ranges, schema=["start_of_month", "end_of_month", "inflation_factor"])

# Create a roster from input file 
roster = get_roster(ROSTER_PATH)


# Cross join to roster
forecast_base = forecast_base.join(roster, how="cross")

# TODO Implement the following for forecast base
# Get prorated portion of month
# Get headcount at end of month
# Calculate monthly salary
# Calculate monthly bonus
# Calculate monthly Commission
# Calculate YTD Cash Compensation

# TODO Implement additional calculations
# Function to add flat monthly fringe amounts (e.g. per head health insurance)
# Function to add fixed rate of compensation fringe (e.g. 401K match)
# Function to add capped rate of compensation fringe (e.g. FUTA tax)

with pl.Config(tbl_cols=-1):
    print(forecast_base)
    print(forecast_base.filter(pl.col("Role ID") < 3))