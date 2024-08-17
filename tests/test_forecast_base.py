import sys
import os
import polars as pl
import pytest
from datetime import date

# Add the src directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Import the function to be tested
from forecast import generate_forecast_base


# Mock Data for Testing
def mock_get_roster(path):
    # Mock a small roster DataFrame
    data = {
        "Employee ID": ["E001", "E002", "E002"],
        "Role ID": [1, 2, 3],
        "start_date_complete": [
            date(2023, 1, 15),
            date(2023, 2, 20),
            date(2023, 1, 20),
        ],
        "end_date_complete": [
            date(2024, 12, 31),
            date(2025, 11, 30),
            date(2025, 11, 30),
        ],
        "Salary": [60000, 75000, 65000],
        "Bonus": [0.1, 0.2, 0.3],
        "Commission": [0.05, 0.0, 0.5],
    }
    return pl.DataFrame(data)


def mock_generate_month_ranges(start_date, end_date, infl_rate, infl_start, infl_freq):
    # Mock some month ranges for testing
    data = {
        "start_of_month": [date(2024, 1, 1), date(2024, 2, 1)],
        "end_of_month": [date(2024, 1, 31), date(2024, 2, 29)],
        "inflation_factor": [1.0, 1.03],
    }
    return pl.DataFrame(data)


# Integration Test for generate_forecast_base
def test_generate_forecast_base(monkeypatch):
    # Use monkeypatch to replace the actual get_roster and generate_month_ranges functions with mocks
    monkeypatch.setattr("forecast.get_roster", mock_get_roster)
    monkeypatch.setattr("forecast.generate_month_ranges", mock_generate_month_ranges)

    # Define inputs
    start_date = date(2024, 1, 1)
    end_date = date(2024, 2, 29)
    infl_rate = 0.03
    infl_start = date(2024, 1, 1)
    infl_freq = 12

    # Generate the forecast base
    forecast_base = generate_forecast_base(
        start_date, end_date, infl_rate, infl_start, infl_freq
    )

    # Check if the output DataFrame has the expected shape and columns
    assert forecast_base.shape == (6, 19)
    expected_columns = {
        "start_of_month",
        "end_of_month",
        "inflation_factor",
        "Employee ID",
        "Role ID",
        "start_date_complete",
        "end_date_complete",
        "Salary",
        "Bonus",
        "Commission",
        "headcount",
        "headcount_change",
        "salary_amount",
        "bonus_amount",
        "commission_amount",
        "compensation",
        "ytd_compensation",
        "proration",
        "year",
    }  # Use set because order is not so important

    assert set(forecast_base.columns) == expected_columns

    assert forecast_base["proration"].to_list() == pytest.approx(
        [1, 1, 1, 1, 1, 1], rel=1e-2
    )
    assert forecast_base["headcount"].to_list() == [1, 1, 1, 1, 1, 1]
    assert forecast_base["compensation"].sum() > 0
    assert (forecast_base["ytd_compensation"] >= forecast_base["compensation"]).all()
    assert (
        (
            forecast_base["salary_amount"]
            + forecast_base["bonus_amount"]
            + forecast_base["commission_amount"]
        )
        == forecast_base["compensation"]
    ).all()


if __name__ == "__main__":
    pytest.main()
