# forecast_menu.py:
from datetime import datetime

import cli.input_handlers as input_handlers
from forecast.base import generate_forecast_base
from forecast.utilities import RosterFileError
from forecast.calculations import rate_forecast, capped_rate_forecast, per_head_forecast


def create_forecast_base(action_register):
    # Prompt user for inputs
    print("Please select a roster file.")

    roster_file = input_handlers.prompt_input_file()
    start_date = input_handlers.prompt_date("Enter the start date (YYYY-MM-DD): ")
    end_date = input_handlers.prompt_date("Enter the end date (YYYY-MM-DD): ")
    inflation_rate = input_handlers.prompt_float(
        "Enter the inflation rate (e.g., 0.03 for 3%): "
    )
    inflation_start = input_handlers.prompt_date(
        "Enter the inflation start date (YYYY-MM-DD): "
    )
    inflation_freq = input_handlers.prompt_positive_integer(
        "Enter the inflation frequency in months: "
    )

    # TODO Comment out test inputs
    # roster_file = 'C:/Users/dunag/python_projects/Headcount-Model/data/Personnel forecast - Personnel List.csv'
    # start_date = datetime(year=2024, month=1, day=1)
    # end_date = datetime(year=2028, month=12, day=31)
    # inflation_rate = 0.03
    # inflation_start = datetime(year=2025, month=1, day=1)
    # inflation_freq = 12

    forecast_base = None

    # Create forecast base using provided inputs
    try:
        forecast_base = generate_forecast_base(
            roster_path=roster_file,
            start_date=start_date,
            end_date=end_date,
            infl_rate=inflation_rate,
            infl_start=inflation_start,
            infl_freq=inflation_freq,
        )

        # Proceed with forecast logic if successful
        print("\nNew Forecast created successfully!\n")

    except RosterFileError as e:
        # Handle roster file error and provide user feedback
        print(
            f"Error in input roster file:\n\n {e}\n\nPlease update file and try again.\n"
        )
    except Exception as e:
        # print(f"Unexpected error: {type(e).__name__} - {e}")
        print(
            f"Unexpected error while creating forecast base: \n\n {e}\n\nPlease check your inputs and try again.\n"
        )

    action_register["base_inputs"] = {
        "roster_file": roster_file,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "inflation_rate": inflation_rate,
        "inflation_start": inflation_start.strftime("%Y-%m-%d"),
        "inflation_freq": inflation_freq,
    }

    return forecast_base


def add_forecast_options(forecast, action_register):
    print("1. Add Flat Rate Forecast")
    print("2. Add Capped Rate Forecast")
    print("3. Add Per Head Forecast")
    choice = input("Enter your choice: ").strip()

    if choice == "1":
        print_cols(forecast)
        # Get inputs
        base_column = input_handlers.prompt_string("Enter base column name: ")
        new_column_name = input_handlers.prompt_string("Enter new column name: ")
        applied_rate = input_handlers.prompt_float(
            "Enter applicable rate (e.g., 0.03 for 3%): "
        )
        # Call function to add flat rate forecast
        forecast = rate_forecast(forecast, base_column, new_column_name, applied_rate)

        # Add step taken to action register
        action_register["added_columns"].append(
            {
                "type": "flat_rate",
                "base_column": base_column,
                "new_column_name": new_column_name,
                "applied_rate": applied_rate,
            }
        )

    elif choice == "2":
        print_cols(forecast)
        # Get inputs
        base_column = input_handlers.prompt_string("Enter base column name: ")
        new_column_name = input_handlers.prompt_string("Enter new column name: ")
        cap_base_column = input_handlers.prompt_string(
            "Enter cap calculation column name: "
        )
        applied_rate = input_handlers.prompt_float(
            "Enter applicable rate (e.g., 0.03 for 3%): "
        )
        cap_amount = input_handlers.prompt_positive_integer(
            "Enter maximum cap amount as integer: "
        )
        # Call function to add capped rate forecast
        forecast = capped_rate_forecast(
            forecast,
            base_column,
            new_column_name,
            applied_rate,
            cap_base_column,
            cap_amount,
        )

        # Add step taken to action register
        action_register["added_columns"].append(
            {
                "type": "capped_rate",
                "base_column": base_column,
                "new_column_name": new_column_name,
                "applied_rate": applied_rate,
                "cap_base_column": cap_base_column,
                "cap_amount": cap_amount,
            }
        )

    elif choice == "3":
        print_cols(forecast)
        # Get inputs
        new_column_name = input_handlers.prompt_string("Enter new column name: ")
        amount = input_handlers.prompt_float("Enter per head amount: ")
        # Call function to add per head forecast
        forecast = per_head_forecast(forecast, new_column_name, amount)

        # Add step taken to action register
        action_register["added_columns"].append(
            {
                "type": "per_head",
                "new_column_name": new_column_name,
                "amount": amount,
            }
        )

    else:
        print("Invalid choice, returning to menu.")

    return forecast


def export_forecast(forecast):
    # Export the forecast to a selected file
    export_path = (
        input_handlers.prompt_export_path()
        + "/"
        + datetime.today().strftime("%y-%m-%d")
        + "_forecast.csv"
    )
    forecast.write_csv(export_path)
    return export_path


def print_cols(forecast):
    """
    Input - Polars DataFrame
    Prints column names and data types
    """

    cols = zip(forecast.columns, forecast.dtypes)

    print("Column", " " * 50, "Dtype")
    print("-" * 64)
    for column in cols:
        print(
            column[0], " " * (62 - len(str(column[0])) - len(str(column[1]))), column[1]
        )
