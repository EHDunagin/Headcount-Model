# Forecast Module

The `forecast` module contains the core functionality of the headcount forecasting application. It provides functions to generate a base forecast, apply various calculations, and handle utility operations for the forecasting process.

## Structure

The module is organized into the following files:

1. **`base.py`** - Defines the primary forecast generation function, along with helper functions to calculate headcount, proration, and compensation.
2. **`calculations.py`** - Contains functions to apply different types of forecast calculations, including rate-based forecasts, capped rates, and per-head costs.
3. **`utilities.py`** - Provides utility functions for reading the headcount roster and generating date ranges with inflation adjustments.

## Functions

### `base.py`

This file contains functions that operate on a forecast base to add calculated columns for headcount, compensation, and more.

- **`generate_forecast_base`**: Generates a base forecast DataFrame by cross-joining the headcount roster with a monthly date range, applying inflation factors, and calculating proration and compensation.

  **Parameters:**
  - `roster_path` (str): Path to the roster CSV file.
  - `start_date` (date): Start date for the forecast.
  - `end_date` (date): End date for the forecast.
  - `infl_rate` (float): Inflation rate.
  - `infl_start` (date): Start date for inflation.
  - `infl_freq` (int): Frequency (in months) of inflation adjustments.

- **`add_year_column`**: Adds a year column based on the start of each month.
- **`add_proration`**: Calculates the active days (proration) for each row.
- **`add_headcount_column`**: Adds a headcount column with 1 if an employee is active in a given month.
- **`add_headcount_change_column`**: Calculates changes in headcount based on employee start and end dates.
- **`calculate_compensation`**: Calculates monthly salary, bonus, and commission amounts, adjusting for proration and inflation.
- **`calculate_ytd_compensation`**: Computes year-to-date compensation.
- **`filter_active_months`**: Filters the DataFrame to include only active months for each employee.

### `calculations.py`

This file includes functions to add new calculated columns to the forecast based on different financial metrics.

- **`rate_forecast`**: Adds a new column based on a percentage of an existing column.

  **Parameters:**
  - `forecast` (DataFrame): The forecast DataFrame.
  - `base_column` (str): Column to calculate the percentage of.
  - `new_column_name` (str): Name for the new column.
  - `applied_rate` (float): Percentage rate to apply.

- **`capped_rate_forecast`**: Similar to `rate_forecast`, but with a cap applied to the base amount.

  **Parameters:**
  - `cap_base_column` (str): Column used to determine if the cap is exceeded.
  - `cap_amount` (float): Maximum cap amount.

- **`per_head_forecast`**: Adds a flat amount adjusted for inflation to the forecast for each month an employee is active, applying it only to rows with the maximum proration per employee and month to avoid duplicating expense in cases where an employee changed roles mid-month.

  **Parameters:**
  - `new_column_name` (str): Name for the new column.
  - `amount` (float): Flat monthly amount to apply.

### `utilities.py`

Contains helper functions for generating date ranges and loading the roster.

- **`increase_date`**: Increases a date by a specified number of months.
- **`generate_month_ranges`**: Generates monthly ranges with inflation adjustments based on the start and end dates, inflation rate, start date for inflation, and frequency of adjustments.

  **Parameters:**
  - `start_date` (date): Start date of the forecast.
  - `end_date` (date): End date of the forecast.
  - `inflation_rate` (float): Rate of inflation.
  - `inflation_date` (date): Date when inflation begins.
  - `inflation_frequency` (int): Number of months between inflation increases.

- **`get_roster`**: Reads the roster CSV, setting missing start and end dates as needed and returns a Polars DataFrame.

## Usage

The primary entry point for generating a forecast is the `generate_forecast_base` function in `base.py`. Start by providing a roster file and forecast parameters (dates, inflation rate, etc.) to generate a detailed forecast.

Once the forecast base is generated, you can apply additional calculations using functions from `calculations.py` to add custom rate-based or per-head forecasts.

## Example
```
from datetime import date
from forecast.base import generate_forecast_base
from forecast.calculations import rate_forecast, per_head_forecast

# Generate the base forecast
forecast = generate_forecast_base(
    roster_path="path/to/roster.csv",
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    infl_rate=0.03,
    infl_start=date(2024, 6, 1),
    infl_freq=12
)

# Add a rate-based forecast column
forecast = rate_forecast(forecast, base_column="salary_amount", new_column_name="taxes", applied_rate=0.2)

# Add a per-head forecast column
forecast = per_head_forecast(forecast, new_column_name="monthly_benefit", amount=500)

# The modified forecast DataFrame can now be exported or further analyzed
```
