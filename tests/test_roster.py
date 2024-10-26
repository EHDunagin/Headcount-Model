import pytest

from datetime import date
from utilities import get_roster

from polars.exceptions import ComputeError, ColumnNotFoundError


def create_temp_csv(tmp_path, content):
    csv_path = tmp_path / "test_roster.csv"
    csv_path.write_text(content)
    return csv_path


def test_get_roster_basic(tmp_path):
    content = """Role ID,Employee ID,Employee Name,Title,Department,Employment type,Location,Start Date,End Date,Salary,Bonus,Commission
1,123,John Doe,Engineer,Engineering,Full-time,New York,01/01/23,,60000,5000,2000
2,124,Jane Smith,Manager,Sales,Part-time,San Francisco,03/15/23,12/31/23,80000,7000,3000
"""
    csv_path = create_temp_csv(tmp_path, content)
    roster = get_roster(csv_path)

    assert roster.shape == (2, 14)
    assert roster["Role ID"][0] == 1
    assert roster["Employee ID"][0] == "123"
    assert roster["Start Date"][0] == date(2023, 1, 1)
    assert roster["End Date"][0] is None
    assert roster["start_date_complete"][0] == date(2023, 1, 1)
    assert roster["end_date_complete"][0] == date.max


def test_get_roster_with_invalid_dates(tmp_path):
    content = """Role ID,Employee ID,Employee Name,Title,Department,Employment type,Location,Start Date,End Date,Salary,Bonus,Commission
1,123,John Doe,Engineer,Engineering,Full-time,New York,01/01/23,invalid_date,60000,5000,2000
2,124,Jane Smith,Manager,Sales,Part-time,San Francisco,03/15/23,12/31/23,80000,7000,3000
"""
    csv_path = create_temp_csv(tmp_path, content)
    roster = get_roster(csv_path)

    assert roster.shape == (2, 14)
    assert roster["Role ID"][0] == 1
    assert roster["Employee ID"][0] == "123"
    assert roster["Start Date"][0] == date(2023, 1, 1)
    assert roster["End Date"][0] is None
    assert roster["start_date_complete"][0] == date(2023, 1, 1)
    assert roster["end_date_complete"][0] == date.max


def test_get_roster_with_empty_dates(tmp_path):
    content = """Role ID,Employee ID,Employee Name,Title,Department,Employment type,Location,Start Date,End Date,Salary,Bonus,Commission
1,123,John Doe,Engineer,Engineering,Full-time,New York,,,60000,5000,2000
2,124,Jane Smith,Manager,Sales,Part-time,San Francisco,03/15/23,12/31/23,80000,7000,3000
"""
    csv_path = create_temp_csv(tmp_path, content)
    roster = get_roster(csv_path)

    assert roster.shape == (2, 14)
    assert roster["Role ID"][0] == 1
    assert roster["Employee ID"][0] == "123"
    assert roster["Start Date"][0] is None
    assert roster["End Date"][0] is None
    assert roster["start_date_complete"][0] == date.min
    assert roster["end_date_complete"][0] == date.max


def test_get_roster_with_mixed_date_formats(tmp_path):
    content = """Role ID,Employee ID,Employee Name,Title,Department,Employment type,Location,Start Date,End Date,Salary,Bonus,Commission
1,123,John Doe,Engineer,Engineering,Full-time,New York,01/01/23,3/15/24,60000,5000,2000
2,124,Jane Smith,Manager,Sales,Part-time,San Francisco,03/15/23,12/31/23,80000,7000,3000
"""
    csv_path = create_temp_csv(tmp_path, content)
    roster = get_roster(csv_path)

    assert roster.shape == (2, 14)
    assert roster["Role ID"][0] == 1
    assert roster["Employee ID"][0] == "123"
    assert roster["Start Date"][0] == date(2023, 1, 1)
    assert roster["End Date"][0] == date(2024, 3, 15)
    assert roster["start_date_complete"][0] == date(2023, 1, 1)
    assert roster["end_date_complete"][0] == date(2024, 3, 15)


def test_get_roster_missing_columns(tmp_path):
    # Missing the 'Role ID' column
    content = """Employee ID,Employee Name,Title,Department,Employment type,Location,Start Date,End Date,Salary,Bonus,Commission
123,John Doe,Engineer,Engineering,Full-time,New York,01/01/23,,60000,5000,2000
124,Jane Smith,Manager,Sales,Part-time,San Francisco,03/15/23,12/31/23,80000,7000,3000
"""
    csv_path = create_temp_csv(tmp_path, content)

    with pytest.raises(
        ColumnNotFoundError, match='unable to find column "([^"]+)"; valid columns:'
    ):
        get_roster(csv_path)


def test_get_roster_invalid_data_types(tmp_path):
    # 'Salary' contains invalid data (string instead of float)
    content = """Role ID,Employee ID,Employee Name,Title,Department,Employment type,Location,Start Date,End Date,Salary,Bonus,Commission
1,123,John Doe,Engineer,Engineering,Full-time,New York,01/01/23,,not_a_number,5000,2000
2,124,Jane Smith,Manager,Sales,Part-time,San Francisco,03/15/23,12/31/23,80000,7000,3000
"""
    csv_path = create_temp_csv(tmp_path, content)

    with pytest.raises(
        ComputeError,
        match="could not parse `([^`]+)` as dtype `([^`]+)` at column '([^']+)'",
    ):
        get_roster(csv_path)


def test_get_roster_missing_file(tmp_path):
    # Simulate an unknown error by providing an invalid file path
    csv_path = tmp_path / "non_existent_file.csv"

    with pytest.raises(
        FileNotFoundError, match="The system cannot find the file specified"
    ):
        get_roster(csv_path)
