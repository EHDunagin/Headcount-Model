from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

import cli.input_handlers as input_handlers
from forecast.base import generate_forecast_base
from forecast.calculations import rate_forecast, capped_rate_forecast, per_head_forecast
from polars.exceptions import ComputeError, ColumnNotFoundError

console = Console()


def create_forecast_base(action_register):
    # Prompt user for inputs
    console.print(Panel("Please select a roster file.", style="bold cyan"))
    roster_file = input_handlers.prompt_input_file()
    start_date = input_handlers.prompt_date("Enter the start date (YYYY-MM-DD): ")
    end_date = input_handlers.prompt_date("Enter the end date (YYYY-MM-DD): ")
    inflation_start = input_handlers.prompt_date(
        "Enter the inflation start date (YYYY-MM-DD): "
    )
    inflation_rate = input_handlers.prompt_float(
        "Enter the inflation rate (e.g., 0.03 for 3%): "
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
        console.print("\n[green]New Forecast created successfully![/green]\n")

    # Handle errors and provide user feedback
    except ComputeError as e:
        console.print(
            f"[red bold]Error in input roster file:[/red bold] {e}\n[red]Check that all columns contain proper data types and update the file.[/red]"
        )
    except ColumnNotFoundError as e:
        console.print(
            f"[red bold]Error in input roster file:[/red bold] {e}\n[red]Ensure all required columns exist and try again.[/red]"
        )
    except Exception as e:
        console.print(
            f"[red bold]Unexpected error:[/red bold] {type(e).__name__} - {e}\n[red]Please check your inputs and try again.[/red]"
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
    table = Table(title="Forecast Options", box=box.ROUNDED, style="bold cyan")
    table.add_column("Option", justify="center", style="bold yellow")
    table.add_column("Description", justify="left", style="white")

    table.add_row("1", "Add Flat Rate Forecast")
    table.add_row("2", "Add Capped Rate Forecast")
    table.add_row("3", "Add Per Head Forecast")

    console.print(table)
    choice = Prompt.ask(
        "[bold cyan]Enter your choice[/bold cyan]", choices=["1", "2", "3"]
    )

    if choice == "1":
        print_cols(forecast)
        base_column = input_handlers.prompt_string("Enter base column name: ")
        new_column_name = input_handlers.prompt_string("Enter new column name: ")
        applied_rate = input_handlers.prompt_float(
            "Enter applicable rate (e.g., 0.03 for 3%): "
        )
        try:
            forecast = rate_forecast(
                forecast, base_column, new_column_name, applied_rate
            )
        except ValueError as err:
            console.print(
                f"[red]Invalid inputs: Forecast could not be added.[/red] {err}"
            )
        else:
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
        try:
            forecast = capped_rate_forecast(
                forecast,
                base_column,
                new_column_name,
                applied_rate,
                cap_base_column,
                cap_amount,
            )
        except ValueError as err:
            console.print(
                f"[red]Invalid inputs: Forecast could not be added.[/red] {err}"
            )
        else:
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
        new_column_name = input_handlers.prompt_string("Enter new column name: ")
        amount = input_handlers.prompt_float("Enter per head amount: ")
        forecast = per_head_forecast(forecast, new_column_name, amount)

        action_register["added_columns"].append(
            {
                "type": "per_head",
                "new_column_name": new_column_name,
                "amount": amount,
            }
        )

    return forecast


def export_forecast(forecast):
    """
    Export the forecast to a selected location as a csv file
    """
    console.print(
        "\n[cyan bold]Please select directory to create forecast.[/cyan bold]\n"
    )
    export_path = (
        input_handlers.prompt_export_path()
        + "/"
        + datetime.today().strftime("%y-%m-%d")
        + "_forecast.csv"
    )
    forecast.write_csv(export_path)
    console.print(f"[green]Forecast exported successfully to {export_path}[/green]")
    return export_path


def print_cols(forecast):
    """
    Input - Polars DataFrame
    Prints column names and data types
    """
    table = Table(title="Forecast Columns", box=box.SIMPLE, style="bold green")
    table.add_column("Column Name", justify="left", style="white")
    table.add_column("Data Type", justify="center", style="yellow")

    for column, dtype in zip(forecast.columns, forecast.dtypes):
        table.add_row(column, str(dtype))

    console.print(table)
