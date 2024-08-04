import pytest
import polars as pl
from datetime import datetime, date

from src.forecast import (
    add_year_column,
    get_proration,
    add_headcount_column,
    add_headcount_change_column,
    calculate_compensation,
    calculate_ytd_compensation,
    filter_active_months,
)

def create_test_forecast_base():
    """ Helper function to create a test forecast_base DataFrame """
    data = {
        "start_of_month": [datetime(2024, 1, 1), datetime(2024, 2, 1), datetime(2024, 3, 1)],
        "end_of_month": [datetime(2024, 1, 31), datetime(2024, 2, 28), datetime(2024, 3, 31)],
        "inflation_factor": [1.0, 1.03, 1.06],
        "start_date_complete": [datetime(2024, 1, 15), datetime(2024, 1, 15) , datetime(2024, 1, 15)],
        "end_date_complete": [datetime(2024, 3, 15), datetime(2024, 3, 15), datetime(2024, 3, 15)],
        "Salary": [60000.0, 60000.0, 60000.0],
        "Bonus": [0.1, 0.1, 0.1],
        "Commission": [0.05, 0.05, 0.05],
        "Employee ID": ["E001", "E001", "E001"]
    }
    return pl.DataFrame(data)

def test_add_year_column():
    forecast_base = create_test_forecast_base()
    result = add_year_column(forecast_base)
    expected_years = [2024, 2024, 2024]
    assert result["year"].to_list() == expected_years

def test_get_proration():
    forecast_base = create_test_forecast_base()
    result = get_proration(forecast_base)
    expected_prorations = [17/31, 1, 15/31]  # Assuming simple calculation for test
    result_list =  result["proration"].to_list() 
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
        pl.Series(name="proration", values=[17/31, 1, 15/31])
    )
    result = calculate_compensation(forecast_base)
    expected_salary = [60000 * 17/31 / 12, 60000 * 1 / 12, 60000 * 15/31 / 12]
    expected_bonus = [6000 * 17/31 / 12, 6000 * 1 / 12, 6000 * 15/31 / 12]
    expected_commission = [3000 * 17/31 / 12, 3000 * 1 / 12, 3000 * 15/31 / 12]
    expected_compensation = [a + b + c for a, b, c in zip(expected_salary, expected_bonus, expected_commission)]
    assert result["salary_amount"].to_list() == pytest.approx(expected_salary, rel=1e-2)
    assert result["bonus_amount"].to_list() == pytest.approx(expected_bonus, rel=1e-2)
    assert result["commission_amount"].to_list() == pytest.approx(expected_commission, rel=1e-2)
    assert result["compensation"].to_list() == pytest.approx(expected_compensation, rel=1e-2)

# def test_calculate_ytd_compensation():
#     forecast_base = create_test_forecast_base()
#     forecast_base = calculate_compensation(forecast_base)  # Calculate compensation first
#     result = calculate_ytd_compensation(forecast_base)
#     comp = forecast_base["compensation"].to_list()
#     expected_ytd_compensation = [sum(comp[:i+1]) for i in range(len(comp))]
#     assert result["ytd_compensation"].to_list() == pytest.approx(expected_ytd_compensation, rel=1e-2)

# def test_filter_active_months():
#     forecast_base = create_test_forecast_base()
#     result = filter_active_months(forecast_base)
#     assert len(result) == 3  # All months are active in this simple test case

# if __name__ == "__main__":
#     pytest.main()
