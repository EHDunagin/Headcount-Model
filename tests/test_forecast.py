import pytest
import polars as pl

from polars.testing import assert_frame_equal, assert_series_equal
from datetime import datetime

from src.forecast import (
    add_year_column,
    add_proration,
    add_headcount_column,
    add_headcount_change_column,
    calculate_compensation,
    calculate_ytd_compensation,
    filter_active_months,
    rate_forecast,
    capped_rate_forecast,
    per_head_forecast,
)


def create_test_forecast_base():
    """Helper function to create a test forecast_base DataFrame"""
    data = {
        "start_of_month": [
            datetime(2024, 1, 1),
            datetime(2024, 2, 1),
            datetime(2024, 3, 1),
        ],
        "end_of_month": [
            datetime(2024, 1, 31),
            datetime(2024, 2, 29),
            datetime(2024, 3, 31),
        ],
        "inflation_factor": [1.0, 1.03, 1.06],
        "start_date_complete": [
            datetime(2024, 1, 15),
            datetime(2024, 1, 15),
            datetime(2024, 1, 15),
        ],
        "end_date_complete": [
            datetime(2024, 3, 15),
            datetime(2024, 3, 15),
            datetime(2024, 3, 15),
        ],
        "Salary": [60000.0, 60000.0, 60000.0],
        "Bonus": [0.1, 0.1, 0.1],
        "Commission": [0.05, 0.05, 0.05],
        "Employee ID": ["E001", "E001", "E001"],
    }
    return pl.DataFrame(data)


def test_add_year_column():
    forecast_base = create_test_forecast_base()
    result = add_year_column(forecast_base)
    expected_years = [2024, 2024, 2024]
    assert result["year"].to_list() == expected_years


def test_add_proration():
    forecast_base = create_test_forecast_base()
    result = add_proration(forecast_base)
    expected_prorations = [17 / 31, 1, 15 / 31]  # Assuming simple calculation for test
    result_list = result["proration"].to_list()
    # Need to divide by 1000 because test df is not counting datetime in ms
    assert result_list[0] / 1000 == pytest.approx(expected_prorations[0], rel=1e-2)
    assert result_list[1] / 1000 == pytest.approx(expected_prorations[1], rel=1e-2)
    assert result_list[2] / 1000 == pytest.approx(expected_prorations[2], rel=1e-2)


def test_add_headcount_column():
    forecast_base = create_test_forecast_base()
    result = add_headcount_column(forecast_base)
    expected_headcount = [1, 1, 0]
    assert result["headcount"].to_list() == expected_headcount


def test_add_headcount_change_column():
    forecast_base = create_test_forecast_base()
    result = add_headcount_change_column(forecast_base)
    expected_changes = [1, 0, -1]
    assert result["headcount_change"].to_list() == expected_changes


def test_calculate_compensation():
    forecast_base = create_test_forecast_base().with_columns(
        pl.Series(name="proration", values=[17 / 31, 1, 15 / 31])
    )
    result = calculate_compensation(forecast_base)

    expected_salary = [
        60000 * 17 / 31 / 12,
        60000 * 1 * 1.03 / 12,
        60000 * 15 / 31 * 1.06 / 12,
    ]
    expected_bonus = [
        6000 * 17 / 31 / 12,
        6000 * 1 * 1.03 / 12,
        6000 * 15 / 31 * 1.06 / 12,
    ]
    expected_commission = [
        3000 * 17 / 31 / 12,
        3000 * 1 * 1.03 / 12,
        3000 * 15 / 31 * 1.06 / 12,
    ]
    expected_compensation = [
        a + b + c
        for a, b, c in zip(expected_salary, expected_bonus, expected_commission)
    ]

    # Check first row
    assert result["salary_amount"].to_list()[0] == pytest.approx(
        expected_salary[0], rel=1e-2
    )
    assert result["bonus_amount"].to_list()[0] == pytest.approx(
        expected_bonus[0], rel=1e-2
    )
    assert result["commission_amount"].to_list()[0] == pytest.approx(
        expected_commission[0], rel=1e-2
    )
    assert result["compensation"].to_list()[0] == pytest.approx(
        expected_compensation[0], rel=1e-2
    )
    # Check second row
    assert result["salary_amount"].to_list()[1] == pytest.approx(
        expected_salary[1], rel=1e-2
    )
    assert result["bonus_amount"].to_list()[1] == pytest.approx(
        expected_bonus[1], rel=1e-2
    )
    assert result["commission_amount"].to_list()[1] == pytest.approx(
        expected_commission[1], rel=1e-2
    )
    assert result["compensation"].to_list()[1] == pytest.approx(
        expected_compensation[1], rel=1e-2
    )
    # Check third row
    assert result["salary_amount"].to_list()[2] == pytest.approx(
        expected_salary[2], rel=1e-2
    )
    assert result["bonus_amount"].to_list()[2] == pytest.approx(
        expected_bonus[2], rel=1e-2
    )
    assert result["commission_amount"].to_list()[2] == pytest.approx(
        expected_commission[2], rel=1e-2
    )
    assert result["compensation"].to_list()[2] == pytest.approx(
        expected_compensation[2], rel=1e-2
    )


def test_calculate_ytd_compensation():
    # Test dataframe with limited info
    data = {
        "start_of_month": [
            datetime(2024, 1, 1),
            datetime(2024, 2, 1),
            datetime(2024, 3, 1),
            datetime(2024, 1, 1),
            datetime(2024, 2, 1),
            datetime(2025, 3, 1),
        ],
        "year": [2024, 2024, 2024, 2024, 2024, 2025],
        "Employee ID": ["E001", "E001", "E001", "E002", "E002", "E002"],
        "compensation": [500, 1000, 1000, 1000, 1000, 1000],
    }
    compensation_df = pl.DataFrame(data)

    # call funciton to test
    result = calculate_ytd_compensation(compensation_df)

    # calculate expected valuse
    comp = compensation_df["compensation"].to_list()
    expected_ytd_compensation = [sum(comp[: i + 1]) for i in range(len(comp))]

    assert result["ytd_compensation"].to_list()[0] == pytest.approx(
        expected_ytd_compensation[0], rel=1e-2
    )
    assert result["ytd_compensation"].to_list()[1] == pytest.approx(
        expected_ytd_compensation[1], rel=1e-2
    )
    assert result["ytd_compensation"].to_list()[2] == pytest.approx(
        expected_ytd_compensation[2], rel=1e-2
    )


def test_filter_active_months():
    forecast_base = create_test_forecast_base()
    # Update start and end dates to ensure that starts and ends are filtered out
    forecast_base[0, "start_date_complete"] = datetime(2024, 2, 1)
    forecast_base[2, "end_date_complete"] = datetime(2024, 2, 29)

    result = filter_active_months(forecast_base)

    # One row, originally the second row, should be retained
    assert len(result) == 1
    assert result[0, "inflation_factor"] == 1.03


def create_test_forecast():
    """Helper function to create a test forecast DataFrame"""
    data = {
        "compensation": [1000.0, 2000.0, 3000.0],
        "ytd_compensation": [150000.0, 169000.0, 175000.0],
        "bonus": [100.0, 200.0, 300.0],
        "headcount": [1, 1, 1],
    }
    return pl.DataFrame(data)


def test_rate_forecast_valid_column():
    forecast = create_test_forecast()
    result = rate_forecast(forecast, "compensation", "new_rate_column", 0.1)
    expected = [100.0, 200.0, 300.0]
    assert result["new_rate_column"].to_list() == expected


def test_rate_forecast_invalid_column():
    forecast = create_test_forecast()
    result = rate_forecast(forecast, "invalid_column", "new_rate_column", 0.1)
    # The original forecast should be returned unchanged
    assert "new_rate_column" not in result.columns
    assert_frame_equal(result, forecast)


def test_rate_forecast_non_numeric_column():
    forecast = create_test_forecast()
    forecast = forecast.with_columns(pl.col("headcount").cast(pl.Utf8))
    result = rate_forecast(forecast, "headcount", "new_rate_column", 0.1)
    # The original forecast should be returned unchanged
    assert "new_rate_column" not in result.columns
    assert_frame_equal(result, forecast)


def test_capped_rate_forecast():
    forecast = create_test_forecast()
    result = capped_rate_forecast(
        forecast,
        base_column="compensation",
        new_column_name="ss_tax",
        applied_rate=0.062,
        cap_base_column="ytd_compensation",
        cap_amount=168600,
    )

    expected = [62.0, 99.2, 0.0]
    assert result["ss_tax"].to_list() == expected

def test_capped_rate_forecast_non_numeric_column():
    forecast = create_test_forecast()
    forecast = forecast.with_columns(pl.col("compensation").cast(pl.Utf8))

    with pytest.raises(ValueError):
        result = capped_rate_forecast(
            forecast,
            base_column="compensation",
            new_column_name="ss_tax",
            applied_rate=0.062,
            cap_base_column="ytd_compensation",
            cap_amount=168600,
        )

def test_per_head_forecast_normal_case():
    # Test the normal case with valid inputs
    df = pl.DataFrame({
        "Employee ID": [1, 1],
        "start_of_month": [
            datetime(2024, 1, 1), 
            datetime(2024, 1, 1)
        ],
        "proration": [0.5, 1.0],
        "inflation_factor": [1.02, 1.02]
    })

    result = per_head_forecast(df, "per_head_amount", 1000)
    expected = pl.Series(name="per_head_amount", values=[0.0, 1020.0])

    assert_series_equal(result["per_head_amount"], expected)


def test_per_head_forecast_missing_columns():
    # Test when required columns are missing
    df = pl.DataFrame({
        "Employee ID": [1],
        "start_of_month": [pl.datetime(2024, 1, 1)]
    })

    with pytest.raises(ValueError, match="column 'proration' or 'inflation_factor' not found or not numeric"):
        per_head_forecast(df, "per_head_amount", 1000)


def test_per_head_forecast_non_numeric_columns():
    # Test when proration or inflation_factor are non-numeric
    df = pl.DataFrame({
        "Employee ID": [1],
        "start_of_month": [datetime(2024, 1, 1)],
        "proration": ["0.5"],
        "inflation_factor": ["1.02"]
    })

    with pytest.raises(ValueError, match="column 'proration' or 'inflation_factor' not found or not numeric"):
        per_head_forecast(df, "per_head_amount", 1000)


def test_per_head_forecast_multiple_roles():
    # Test with an employee having multiple roles in the same month
    df = pl.DataFrame({
        "Employee ID": [1, 1, 2],
        "start_of_month": [datetime(2024, 1, 1), datetime(2024, 1, 1), datetime(2024, 1, 1)],
        "proration": [0.5, 1.0, 0.8],
        "inflation_factor": [1.02, 1.02, 1.02]
    })

    result = per_head_forecast(df, "per_head_amount", 1000)
    expected = pl.Series(name="per_head_amount", values=[0.0, 1020.0, 1020.0])
    
    assert_series_equal(result["per_head_amount"], expected)

def test_per_head_forecast_no_proration():
    # Test when proration is zero
    df = pl.DataFrame({
        "Employee ID": [1],
        "start_of_month": [datetime(2024, 1, 1)],
        "proration": [0],
        "inflation_factor": [1.02]
    })

    result = per_head_forecast(df, "per_head_amount", 1000)
    expected = pl.Series(name="per_head_amount", values=[0.0])
    
    assert_series_equal(result["per_head_amount"], expected)


