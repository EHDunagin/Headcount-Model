# input_handlers.py

import tkinter as tk
from tkinter import filedialog
from datetime import datetime

from rich.console import Console

# Set up Rich Console
console = Console()


def prompt_input_file():
    """
    Prompt the user to select a file using tkinter filedialog.
    Returns the selected file path.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    console.print("[blue]Select the input CSV file.[/blue]")
    file_path = filedialog.askopenfilename(
        title="Select Input CSV File", filetypes=[("CSV files", "*.csv")]
    )
    if not file_path:
        console.print("[red]No file selected. Please try again.[/red]")
        return prompt_input_file()  # Retry if no file selected

    console.print(f"[green]File selected:[/green] {file_path}")
    return file_path


def prompt_input_json():
    """
    Prompt the user to select a file using tkinter filedialog.
    Returns the selected file path.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    console.print("[blue]Select the input JSON file.[/blue]")

    file_path = filedialog.askopenfilename(
        title="Select Input JSON File", filetypes=[("JSON files", "*.json")]
    )
    if not file_path:
        console.print("[red]No file selected. Please try again.[/red]")
        return prompt_input_json()  # Retry if no file selected

    console.print(f"[green]File selected:[/green] {file_path}")
    return file_path


def prompt_export_path():
    """
    Prompt the user to select a directory for exporting the forecast using tkinter filedialog.
    Returns the selected directory path.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    console.print("[blue]Select the export directory.[/blue]")
    directory_path = filedialog.askdirectory(title="Select Export Directory")
    if not directory_path:
        console.print("[red]No directory selected. Please try again.[/red]")
        print("No directory selected, please try again.")
        return prompt_export_path()  # Retry if no directory selected

    console.print(f"[green]Directory selected:[/green] {directory_path}")
    return directory_path


def prompt_date(msg):
    """
    Prompt the user to input a date in YYYY-MM-DD format.
    Returns a datetime.date object.
    """
    date_str = console.input(f"[blue]{msg}[/blue]").strip()
    try:
        start_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return start_date
    except ValueError:
        console.print("[red]Invalid date format. Please use YYYY-MM-DD.[/red]")
        return prompt_date(msg)  # Retry if invalid date


def prompt_positive_integer(prompt_message):
    """
    Generic prompt for an integer input.
    """
    int_str = console.input(f"[blue]{prompt_message}[/blue]").strip()
    try:
        value = int(int_str)
        if value <= 0:
            raise ValueError
        return value
    except ValueError:
        console.print(
            "[red]Invalid input. Please enter a valid positive integer.[/red]"
        )
        return prompt_positive_integer(prompt_message)  # Retry if invalid input


def prompt_float(prompt_message):
    """
    Generic prompt for a float input.
    """
    float_str = console.input(f"[blue]{prompt_message}[/blue]").strip()
    try:
        value = float(float_str)
        return value
    except ValueError:
        console.print("[red]Invalid input. Please enter a valid float.[/red]")
        return prompt_float(prompt_message)  # Retry if invalid input


def prompt_string(prompt_message, max_length=50):
    """
    Generic prompt for a string input with a maximum length of 50 characters.
    """
    user_input = console.input(f"[blue]{prompt_message}[/blue]").strip()
    if len(user_input) > max_length:
        console.print(
            f"[red]Input too long. Please enter a string with a maximum of {max_length} characters.[/red]"
        )
        return prompt_string(prompt_message, max_length)  # Retry if too long

    return user_input
