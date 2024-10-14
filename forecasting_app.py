# forecasting_app.py:

import cli.main_menu as main_menu
import cli.forecast_menu as forecast_menu
import cli.register_menu as register_menu


def main():
    # Initialize an empty forecast (None initially) and action register
    forecast = None
    action_register = None
    while True:
        # Display the main menu and capture the user's choice
        choice = main_menu.display_main_menu()

        if choice == "create_forecast":
            # Set new action register to clear any old steps
            action_register = {
                "base_inputs": {},
                "added_columns": [],
            }
            # Create a new forecast base
            forecast = forecast_menu.create_forecast_base(action_register)

        elif choice == "add_forecast":
            # Ensure a forecast exists before proceeding
            if forecast is not None:
                forecast = forecast_menu.add_forecast_options(forecast, action_register)
            else:
                print("\nPlease create a forecast base first.\n")
        
        elif choice == "forecast_from_file":
            forecast, action_register = register_menu.forecast_from_file()

        elif choice == "export_forecast":
            # Ensure a forecast exists before proceeding
            if forecast is not None:
                export_path = forecast_menu.export_forecast(forecast)
                print(f"Forecast exported to {export_path}")
            else:
                print("\nPlease create a forecast base first.\n")

        elif choice == "export_steps":
            # Ensure an action register exists before proceeding
            if action_register is not None:
                export_path = register_menu.export_register(action_register)
                print(f"Steps exported to {export_path}")
            else:
                print("\nPlease create a forecast first.\n")

        elif choice == "exit":
            print("Exiting program...")
            break


if __name__ == "__main__":
    main()
