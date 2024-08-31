import datetime

from utilities import increase_date


class TestIncrease:
    def test_one_month_in_year(self):
        start_date = datetime.date(year=2024, month=1, day=1)
        new_date = datetime.date(year=2024, month=2, day=1)
        assert increase_date(start_date, 1) == new_date

    def test_mid_year_mid_month(self):
        start_date = datetime.date(year=2024, month=5, day=17)
        new_date = datetime.date(year=2024, month=6, day=1)
        assert increase_date(start_date, 1) == new_date

    def test_multi_month(self):
        start_date = datetime.date(year=2024, month=1, day=1)
        new_date = datetime.date(year=2024, month=8, day=1)
        assert increase_date(start_date, 7) == new_date

    def test_no_months_off_day(self):
        start_date = datetime.date(year=2024, month=3, day=15)
        new_date = datetime.date(year=2024, month=3, day=1)
        assert increase_date(start_date, 0) == new_date

    def test_december_incr_one_month(self):
        start_date = datetime.date(year=2024, month=12, day=1)
        new_date = datetime.date(year=2025, month=1, day=1)
        assert increase_date(start_date, 1) == new_date

    def test_multi_month_incr_roll_year(self):
        start_date = datetime.date(year=2024, month=1, day=1)
        new_date = datetime.date(year=2025, month=7, day=1)
        assert increase_date(start_date, 18) == new_date
