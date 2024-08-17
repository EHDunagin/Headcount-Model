import datetime


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

    while current_date <= end_date:
        # Calculate the first day of the next month
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1)

        # Calculate the last day of the current month
        end_of_month = next_month - datetime.timedelta(days=1)

        # Increment inflation if necessary
        if current_date >= inflation_date:
            inflation_factor *= 1.0 + inflation_rate
            inflation_date = increase_date(inflation_date, inflation_frequency)

        # Append the month range to the list
        month_ranges.append((current_date, end_of_month, inflation_factor))

        # Move to the next month
        current_date = next_month

    return month_ranges
