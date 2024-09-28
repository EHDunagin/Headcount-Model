# main_menu.py:


def display_main_menu():
    print("Main Menu:")
    print("1. Create New Forecast")
    print("2. Add Forecast Options (Flat Rate, Capped Rate, Per Head)")
    print("3. Export Forecast")
    print("4. Exit")

    choice = input("Enter your choice: ").strip()
    if choice == "1":
        return "create_forecast"
    elif choice == "2":
        return "add_forecast"
    elif choice == "3":
        return "export_forecast"
    elif choice == "4":
        return "exit"
    else:
        print("Invalid choice, please try again.")
        return display_main_menu()
