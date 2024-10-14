# record.py:
import json
from datetime import datetime

import cli.input_handlers as input_handlers
from forecast.base import generate_forecast_base
from forecast.utilities import RosterFileError
from forecast.calculations import rate_forecast, capped_rate_forecast, per_head_forecast


def export_register(action_register):
    """
    Export the action_register to a json file in a selected location
    """
    print("\nPlease select directory to create record of action steps. \n")
    
    export_path = (
        input_handlers.prompt_export_path()
        + "/"
        + datetime.today().strftime("%y-%m-%d")
        + "_action_steps.json"
    )

    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(action_register, f, ensure_ascii=False, indent=4)
    
    return export_path

def forecast_from_file():
    """
    Create a forecast from json file of actions.
    """
    print("\nPlease select file of forecast steps in JSON format")
    filepath = input_handlers.prompt_input_json() 
    with open(filepath, 'r') as file:
        actions = json.load(file)
    print(f'Action register  of type {type(actions)} \n\n {actions}')
    forecast = None

    # Create Forecast base
    try:
        forecast = generate_forecast_base(
            roster_path=actions['base_inputs']['roster_file'],
            start_date=datetime.strptime(actions['base_inputs']['start_date'], "%Y-%m-%d").date(),
            end_date=datetime.strptime(actions['base_inputs']['end_date'], "%Y-%m-%d").date(),
            infl_rate=actions['base_inputs']['inflation_rate'],
            infl_start=datetime.strptime(actions['base_inputs']['inflation_start'], "%Y-%m-%d").date(),
            infl_freq=actions['base_inputs']['inflation_freq'],
        )

        # Proceed with forecast logic if successful
        print("\nNew Forecast created successfully!\n")

    except RosterFileError as e:
        print(
            f"Error in input roster file:\n\n {e}\n\nPlease update file and try again.\n"
        )

    except Exception as e:
        print(
            f"Unexpected error while creating forecast base: \n\n {e}\n\nPlease check your inputs and try again.\n"
        )

    if forecast is None:
        return None

    # Create all added columns sequentially in order
    for column in actions['added_columns']:

        if column['type'] == 'flat_rate':
            # Call function to add flat rate forecast
            forecast = rate_forecast(
                forecast, 
                base_column=column['base_column'], 
                new_column_name=column['new_column_name'], 
                applied_rate=column['applied_rate']
            )
            
        elif column['type'] == 'capped_rate':
            # Call function to add capped rate forecast
            forecast = capped_rate_forecast(
                forecast,
                base_column=column['base_column'],
                new_column_name=column['new_column_name'],
                applied_rate=column['applied_rate'],
                cap_base_column=column['cap_base_column'],
                cap_amount=column['cap_amount'],
            )

        elif column['type'] == 'per_head':
            # Call function to add per head forecast
            forecast = per_head_forecast(
                forecast, 
                new_column_name=column['new_column_name'],
                amount=column['amount'],
            )

        else:
            print(f"Unknown column type: {column['type']}\nNo forecast will be added")

    return forecast, actions
    