from Finance_manager import FinanceManager
from transaction import Transaction


def main():
    print("=== Finance Manager ===")
    manager = FinanceManager()

    while True:
        print("\nOptions:")
        print("1. Add Transaction")
        print("2. View Balance")
        print("3. View Detailed Summary")
        print("4. View Category Breakdown")
        print("5. View Transaction History")
        print("6. Set Budget for a Category")
        print("7. Set Savings Goal")
        print("8. Track Savings Progress")
        print("9. Recommend Monthly Savings")
        print("10. View Spending Summary")
        print("11. View Spending Trends")
        print("12. Import transactions from CSV")
        print("13. Import transactions from Json")
        print("14. Export Financial data as Report")
        print("0. Exit")

        choice = input("Enter your choice (1-12): ")

        if choice == "1":
            # Add transaction
            date = input("Enter date (YYYY-MM-DD): ")
            category = input("Enter category (e.g., Food, Rent): ")
            amount = float(input("Enter amount: "))
            transaction_type = input("Is this 'Income' or 'Expense'? ").capitalize()

            while transaction_type not in ["Income", "Expense"]:
                print("Invalid type. Please enter 'Income' or 'Expense'.")
                transaction_type = input("Is this 'Income' or 'Expense'? ").capitalize()

            transaction = Transaction(date, category, amount, transaction_type)
            manager.add_transaction(transaction)

        elif choice == "2":
            # View current balance
            _, _, balance = manager.calculate_summary()
            print(f"\nYour current balance is: ${balance:.2f}")

        elif choice == "3":
            # View detailed summary
            total_income, total_expense, balance = manager.calculate_summary()
            print("\n=== Financial Summary ===")
            print(f"Total Income:   ${total_income:.2f}")
            print(f"Total Expenses: ${total_expense:.2f}")
            print(f"Balance:        ${balance:.2f}")

        elif choice == "4":
            # View category breakdown
            breakdown = manager.category_breakdown()
            print("\n=== Category Breakdown ===")
            for category, values in breakdown.items():
                print(f"{category}: Income = ${values['Income']:.2f}, Expense = ${values['Expense']:.2f}")

        elif choice == "5":
            # View transaction history
            manager.show_transactions()

        elif choice == "6":
            # Set Budget for a category
            category = input("Enter the category for the budget (e.g., Food, Rent): ")
            amount = float(input(f"Enter the budget amount for {category}: $"))
            period = input("Is this budget for 'monthly' or 'weekly'? ").lower()

            manager.set_budget(category, amount, period)

        elif choice == "7":
            # Set Savings Goal
            goal_name = input("Enter the name for the savings goal (e.g., Vacation, Emergency Fund): ")
            target_amount = float(input(f"Enter the target amount for {goal_name}: $"))
            months_to_save = int(input("Enter the number of months to reach this goal: "))
            manager.set_savings_goal(goal_name, target_amount, months_to_save)

        elif choice == "8":
            # Track Savings Progress
            goal_name = input("Enter the name of the savings goal to track: ")
            try:
                manager.track_savings_progress(goal_name)
            except KeyError:
                print(f"No savings goal found with the name '{goal_name}'.")

        elif choice == "9":
            # Recommend Monthly Savings
            goal_name = input("Enter the name of the savings goal for recommendations: ")
            try:
                manager.recommend_monthly_savings(goal_name)
            except KeyError:
                print(f"No savings goal found with the name '{goal_name}'.")

        elif choice == "10":
            # View Spending Summary
            period = input("View spending summary for 'monthly' or 'weekly'? ").lower()
            if period in ["monthly", "weekly"]:
                manager.generate_spending_summary(period)
            else:
                print("Invalid period. Please choose 'monthly' or 'weekly'.")

        elif choice == "11":
            # Generate Spending Trends for Two Periods
            print("Enter details for the first month:")
            year1 = int(input("Year (e.g., 2024): "))
            month1 = int(input("Month (1-12): "))

            print("Enter details for the second month:")
            year2 = int(input("Year (e.g., 2024): "))
            month2 = int(input("Month (1-12): "))

            try:
                manager.generate_spending_trends(year1, month1, year2, month2)
            except ValueError as e:
                print("Invalid input. Please ensure the year and month are correct.")

        elif choice == "12":
            filename = input("Enter the CSV file path: ")
            manager.import_from_csv(filename)       

        elif choice == "13":
            filename = input("Enter the JSON file path: ")
            manager.import_from_json(filename)    

        elif choice == "14":
            # Export Financial Report
            filename = input("Enter filename for the report (default: financial_report.txt): ") or "financial_report.txt"
            manager.export_financial_report(filename) 

        elif choice == "0":
            # Exit the program
            print("Exiting Finance Manager. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 12.")


if __name__ == "__main__":
    main()
