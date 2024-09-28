# forecasting_app.py:

import cli.main_menu as main_menu
import cli.forecast_menu as forecast_menu


def main():
    # Initialize an empty forecast (None initially)
    forecast = None
    while True:
        # Display the main menu and capture the user's choice
        choice = main_menu.display_main_menu()

        if choice == "create_forecast":
            # Create a new forecast base
            forecast = forecast_menu.create_forecast_base()

        elif choice == "add_forecast":
            # Ensure a forecast exists before proceeding
            if not (forecast is None):
                forecast = forecast_menu.add_forecast_options(forecast)
            else:
                print("\nPlease create a forecast base first.\n")

        elif choice == "export_forecast":
            # Ensure a forecast exists before proceeding
            if not (forecast is None):
                export_path = forecast_menu.export_forecast(forecast)
                print(f"Forecast exported to {export_path}")
            else:
                print("\nPlease create a forecast base first.\n")

        elif choice == "exit":
            print("Exiting program...")
            break


if __name__ == "__main__":
    main()
