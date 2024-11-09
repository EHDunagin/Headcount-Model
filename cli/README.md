# CLI Directory

This directory contains the command-line interface (CLI) components for the forecasting application. The CLI enables users to create and modify forecasts through a text-based menu-driven interface. Below is an overview of each file within this directory and its purpose.

## Files

### 1. `forecast_menu.py`

This file handles the creation and modification of forecast bases and forecast options. Key functions include:

- **`create_forecast_base(action_register)`**: Prompts the user for inputs such as the roster file, start date, end date, inflation rate, inflation start date, and inflation frequency. It uses these inputs to generate the initial forecast base.
- **`add_forecast_options(forecast, action_register)`**: Allows users to add forecast calculations to the base forecast. Available options include:
  - Flat Rate Forecast
  - Capped Rate Forecast
  - Per Head Forecast
- **`export_forecast(forecast)`**: Exports the forecast to a CSV file at a specified location.
- **`print_cols(forecast)`**: Prints the column names and data types of a given Polars DataFrame, helping the user understand the structure of the forecast.

### 2. `input_handlers.py`

This file contains utility functions for handling user input, including file selection and input validation:

- **`prompt_input_file()`**: Prompts the user to select a CSV file (for input).
- **`prompt_input_json()`**: Prompts the user to select a JSON file (for loading saved forecasts).
- **`prompt_export_path()`**: Prompts the user to select a directory for exporting forecast files.
- **`prompt_date(msg)`**: Prompts the user to enter a date in `YYYY-MM-DD` format.
- **`prompt_positive_integer(prompt_message)`**: Prompts the user to enter a positive integer.
- **`prompt_float(prompt_message)`**: Prompts the user to enter a floating-point number.
- **`prompt_string(prompt_message, max_length=50)`**: Prompts the user to enter a string, enforcing a maximum character limit.

### 3. `main_menu.py`

This file contains the main menu for the CLI. The `display_main_menu()` function presents options to the user and directs them to different actions within the application based on their selection:

- **Options**:
  1. Create New Forecast
  2. Add Forecast Options (Flat Rate, Capped Rate, Per Head)
  3. Forecast From File
  4. Export Forecast
  5. Export Steps
  6. Exit

### 4. `register_menu.py`

This file handles loading and exporting action steps associated with forecast creation. It enables users to save and restore actions performed during the forecasting process:

- **`export_register(action_register)`**: Exports the action register to a JSON file, allowing users to save the steps they took in creating or modifying a forecast.
- **`forecast_from_file()`**: Reads an action register from a JSON file and replays the steps to recreate a forecast, including creating the base forecast and adding any specified forecast columns (flat rate, capped rate, or per head).

## Usage

The CLI provides a step-by-step interface for creating, modifying, and exporting forecasts. Users can start by creating a new forecast or loading an existing forecast setup from a JSON file. The application allows for adding various forecasting options and exporting the results to CSV format. Additionally, users can save their actions to a JSON file to recreate or modify the forecast later.

### Example Workflow

1. **Create New Forecast**: Select a roster file, input start and end dates, and define inflation parameters.
2. **Add Forecast Options**: Choose from flat rate, capped rate, or per head options to apply specific calculations to the forecast.
3. **Export Forecast**: Save the forecast to a specified location in CSV format.
4. **Export Steps**: Save the action register to a JSON file for future use.
5. **Forecast From File**: Load a saved action register from JSON to recreate or extend a forecast.

## Dependencies

This CLI relies on the following modules:
- `tkinter`: For file dialog prompts.
- `datetime`: For handling dates.
- `polars`: For DataFrame manipulation.
- `json`: For exporting and importing action registers.

## Notes

- Ensure `polars` and `tkinter` are properly installed in your environment.
- The CLI is designed for text-based interaction, so users should be comfortable with command-line navigation.

---

This README provides an overview of the CLI directory's structure and functionality. It can be used to understand the purpose of each component and how to navigate the forecasting application's text interface.
