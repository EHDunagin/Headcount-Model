# Headcount Forecasting Application

A modular application for forecasting headcount, compensation, and other employee-related metrics. This application uses a text-based user interface (TUI) to guide users through creating and exporting forecasts using various forecasting models.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
   - [Main Menu Options](#main-menu-options)
5. [Directory Structure](#directory-structure)
6. [Testing](#testing)
7. [Data](#data)
8. [License](#license)

---

## Overview

The Headcount Forecasting Application is a flexible tool designed to project future headcount costs and other metrics based on user inputs and pre-set models. Through an intuitive TUI, users can:
- Create forecast bases from employee rosters,
- Add forecast adjustments (e.g., rate-based or per-head adjustments),
- Save and export forecast data,
- And document forecast steps in an action register.

## Features

- **Modular Forecasting**: Supports multiple forecast models (e.g., flat rate, capped rate, per head) with customizable inputs.
- **Data Export**: Exports forecasts and steps to files for further analysis.
- **User-Friendly Interface**: Text-based UI for easy navigation and input handling.
- **Action Register**: Tracks and exports the forecast creation steps.

---

## Installation

1. **Clone the Repository**:
   ```
   git clone <repository-url>
   cd headcount-model
   ```

2. **Set up the Python Environment**:
   Install dependencies from `requirements.txt` using:
   ```
   pip install -r requirements.txt
   ```

3. **Verify Installation**:
   Run the application to ensure everything is set up correctly:
   
   ```
   python forecasting_app.py
   ```

---

## Usage

Run the main program from the command line:
```
python forecasting_app.py
```
The application will open with the main menu, from which users can create and modify forecasts, export data, and exit the program.

### Main Menu Options

1. **Create Forecast**: Initializes a new forecast base by prompting for employee roster and forecast parameters.
2. **Add Forecast**: Adds specific expense forecasts (e.g., flat percent of salary, per-head rates).
3. **Forecast from File**: Loads an existing forecast from a saved file.
4. **Export Forecast**: Exports the generated forecast to a specified file path.
5. **Export Steps**: Saves the steps taken to create the forecast in an action register.
6. **Exit**: Exits the application.

---

## Directory Structure

The codebase is organized into modules for modular and easy-to-navigate code.
```
Headcount-Model/
├── forecasting_app.py       # Main entry point for the TUI
├── cli/                     # Directory for the TUI logic
│   ├── main_menu.py         # Main menu functionality
│   ├── input_handlers.py    # Cleaning and validation on user inputs
│   ├── forecast_menu.py     # Forecast-related options and inputs
│   ├── register_menu.py     # Registers for tracking forecast steps
├── forecast/                # Core forecasting logic
│   ├── base.py              # Functions for forecast base creation
│   ├── calculations.py      # Functions for specific forecast models
│   ├── utilities.py         # Utility functions, including CSV handling
├── data/                    # Folder for input and output data
├── tests/                   # Unit tests
│   ├── test_forecast.py     # Tests for forecast functions
│   ├── test_cli.py          # Tests for CLI functionalities
└── requirements.txt         # List of dependencies
```
---

## Testing

Tests are located in the `tests/` directory and use `pytest` for testing. To run all tests:
``` 
pytest tests/
```
Individual modules can also be tested by running specific test files, e.g.:
```
pytest tests/test_forecast.py
```
---
## Data

The application requires a roster file in CSV format containing employee and role information. This file must include the following columns with the specified data types:

| Column           | Description                                                   | Data Type |
|------------------|---------------------------------------------------------------|-----------|
| Role ID          | Unique ID for a position to distinguish different roles a single individual may fill | Integer   |
| Employee ID      | Unique ID for an employee                                     | Text      |
| Employee Name    | Name of the employee                                          | Text      |
| Title            | Job title of the employee                                     | Text      |
| Department       | Department where the employee works                           | Text      |
| Employment Type  | Full-time, part-time, etc.                                    | Text      |
| Location         | Location of the employee                                      | Text      |
| Start Date       | Date the employee started the role                            | Date      |
| End Date         | Date the employee ended the role (if applicable)              | Date      |
| Salary           | Base salary of the employee                                   | Decimal   |
| Bonus            | Bonus as a percentage of the salary                           | Decimal   |
| Commission       | Commission as a percentage of the salary                      | Decimal   |


Ensure that your CSV file includes these columns with the correct data types, as the application relies on this structure for accurate forecasting.



## License

This project is licensed under the MIT License.

--- 
