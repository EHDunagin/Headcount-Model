# main_menu.py
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()


def display_main_menu():
    # Create a styled menu table
    table = Table(title="Main Menu", title_style="bold cyan")
    table.add_column("Option", justify="center", style="bold yellow")
    table.add_column("Action", justify="left", style="bold white")

    table.add_row("1", "Create New Forecast")
    table.add_row("2", "Add Forecast Options (Flat Rate, Capped Rate, Per Head)")
    table.add_row("3", "Forecast From File")
    table.add_row("4", "Export Forecast")
    table.add_row("5", "Export Steps")
    table.add_row("6", "Exit")

    console.print(table)

    # Use Rich's Prompt for input
    choice = Prompt.ask(
        "[bold cyan]Enter your choice[/bold cyan]",
        choices=["1", "2", "3", "4", "5", "6"],
    )

    if choice == "1":
        return "create_forecast"
    elif choice == "2":
        return "add_forecast"
    elif choice == "3":
        return "forecast_from_file"
    elif choice == "4":
        return "export_forecast"
    elif choice == "5":
        return "export_steps"
    elif choice == "6":
        return "exit"
    else:
        print("Invalid choice, please try again.")
        return display_main_menu()
