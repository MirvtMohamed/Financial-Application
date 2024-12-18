import json
import csv
from transaction import Transaction
from collections import defaultdict
from datetime import date, datetime 


class FinanceManager:
    def __init__(self, data_file="transactions.json", budget_file="budgets.json", savings_file="savings_goals.json"):
        self.transactions = []
        self.budgets = {}
        self.savings_goals = {}  # Dictionary to store savings goals
        self.data_file = data_file
        self.budget_file = budget_file
        self.savings_file = savings_file
        self.load_transactions()
        self.load_budgets()
        self.load_savings_goals()
        
    

    def import_from_csv(self, filename):
        """
        Import transaction data from a CSV file.
        Assumes the CSV has columns: date, category, amount, type (Expense or Income)

        Args:
        filename (str): Path to the CSV file to import.
        """
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Assuming the CSV contains 'date', 'category', 'amount', 'transaction_type'
                date = row['date']
                category = row['category']
                amount = float(row['amount'])
                transaction_type = row['transaction_type']

                # Create a Transaction object and add it to the list
                transaction = Transaction(date, category, amount, transaction_type)
                self.transactions.append(transaction)
        print(f"Imported {len(self.transactions)} transactions from {filename}")

    def import_from_json(self, filename):
        """
        Import transaction data from a JSON file.
        Assumes the JSON is a list of transactions, each with: date, category, amount, type (Expense or Income)

        Args:
        filename (str): Path to the JSON file to import.
        """
        with open(filename, 'r') as file:
            data = json.load(file)
            for item in data:
                # Assuming each entry has 'date', 'category', 'amount', 'transaction_type'
                date = item['date']
                category = item['category']
                amount = float(item['amount'])
                transaction_type = item['transaction_type']

                # Create a Transaction object and add it to the list
                transaction = Transaction(date, category, amount, transaction_type)
                self.transactions.append(transaction)
        print(f"Imported {len(self.transactions)} transactions from {filename}")

    def load_transactions(self):
        """Load transactions from the JSON file."""
        try:
            with open(self.data_file, "r") as file:
                data = json.load(file)
                self.transactions = [Transaction.from_dict(t) for t in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.transactions = []

    def save_transactions(self):
        """Save all transactions to the JSON file."""
        with open(self.data_file, "w") as file:
            json.dump([t.to_dict() for t in self.transactions], file, indent=4)

    def load_budgets(self):
        """Load budgets from the JSON file."""
        try:
            with open(self.budget_file, "r") as file:
                self.budgets = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.budgets = {}

    def save_budgets(self):
        """Save all budgets to the JSON file."""
        with open(self.budget_file, "w") as file:
            json.dump(self.budgets, file, indent=4)

    def set_budget(self, category, amount, period="monthly"):
        """Set a budget for a specific category."""
        if period not in ["monthly", "weekly"]:
            print("Invalid period. Please use 'monthly' or 'weekly'.")
            return

        self.budgets[category] = {"amount": amount, "period": period}
        self.save_budgets()
        print(f"Budget for {category} set to ${amount} per {period}.")

    def track_budget_utilization(self, category, period="monthly"):
        """Track budget utilization for a category."""
        if category not in self.budgets:
            print(f"No budget set for category: {category}")
            return 0.0

        # Sum expenses for this category
        total_expenses = sum(t.amount for t in self.transactions if t.category == category and t.transaction_type == "Expense")
        
        budget = self.budgets[category]["amount"]
        utilization = (total_expenses / budget) * 100 if budget > 0 else 0.0
        return utilization

    def check_budget_alerts(self, category):
        """Check if the budget limit is nearing for a category."""
        utilization = self.track_budget_utilization(category)
        budget = self.budgets.get(category, {}).get("amount", 0)

        if utilization > 90:
            print(f"Warning: You have used {utilization:.2f}% of your {category} budget!")
        elif utilization > 75:
            print(f"Alert: You have used {utilization:.2f}% of your {category} budget.")

    def load_savings_goals(self):
        """Load savings goals from the JSON file."""
        try:
            with open(self.savings_file, "r") as file:
                self.savings_goals = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.savings_goals = {}

    def save_savings_goals(self):
        """Save all savings goals to the JSON file."""
        with open(self.savings_file, "w") as file:
            json.dump(self.savings_goals, file, indent=4)

    def set_savings_goal(self, goal_name, target_amount, months_to_save):
        """Set a savings goal with a target amount and time frame (in months)."""
        self.savings_goals[goal_name] = {
            "target_amount": target_amount,
            "months_to_save": months_to_save,
            "saved_amount": 0  # Start with no savings
        }
        self.save_savings_goals()
        print(f"Savings goal for '{goal_name}' set to ${target_amount} in {months_to_save} months.")

    def track_savings_progress(self, goal_name):
        """Track progress towards a savings goal."""
        if goal_name not in self.savings_goals:
            print(f"No savings goal set for '{goal_name}'.")
            return

        saved_amount = self.savings_goals[goal_name]["saved_amount"]
        target_amount = self.savings_goals[goal_name]["target_amount"]
        remaining_amount = target_amount - saved_amount
        print(f"Progress for goal '{goal_name}': ${saved_amount} saved, ${remaining_amount} remaining.")

    def recommend_monthly_savings(self, goal_name):
        """Recommend how much to save monthly to reach the savings goal on time."""
        if goal_name not in self.savings_goals:
            print(f"No savings goal set for '{goal_name}'.")
            return

        goal = self.savings_goals[goal_name]
        target_amount = goal["target_amount"]
        months_to_save = goal["months_to_save"]
        
        monthly_savings = target_amount / months_to_save
        print(f"To reach the goal '{goal_name}', you need to save ${monthly_savings:.2f} each month.")
        return monthly_savings       

    def generate_spending_summary(self, period="monthly"):
        """Generate a summary of spending based on the specified period (monthly or weekly)."""
        total_spent = 0
        category_spending = defaultdict(float)

        for transaction in self.transactions:
            if transaction.transaction_type == "Expense":
                total_spent += transaction.amount
                category_spending[transaction.category] += transaction.amount

        print(f"Total Spending ({period}): ${total_spent:.2f}")
        print("Spending by Category:")
        for category, amount in category_spending.items():
            print(f"{category}: ${amount:.2f}")
        
        return total_spent, category_spending

    def generate_spending_trends(self, year1, month1, year2, month2):
        """
        Generate insights into spending trends for two specific months.

        Args:
            year1 (int): Year of the first month (e.g., 2024).
            month1 (int): Month of the first period (1-12).
            year2 (int): Year of the second month (e.g., 2024).
            month2 (int): Month of the second period (1-12).
        """
        from calendar import monthrange

        # Calculate start and end dates for the two periods
        start_date1 = date(year1, month1, 1)
        end_date1 = date(year1, month1, monthrange(year1, month1)[1])

        start_date2 = date(year2, month2, 1)
        end_date2 = date(year2, month2, monthrange(year2, month2)[1])

        # Filter transactions for the two periods
        period1_transactions = [
            t for t in self.transactions
            if t.transaction_type == "Expense" and start_date1 <= datetime.strptime(t.date, "%Y-%m-%d").date() <= end_date1
        ]
        period2_transactions = [
            t for t in self.transactions
            if t.transaction_type == "Expense" and start_date2 <= datetime.strptime(t.date, "%Y-%m-%d").date() <= end_date2
        ]

        # Calculate spending for each period
        spending_period1 = sum(t.amount for t in period1_transactions)
        spending_period2 = sum(t.amount for t in period2_transactions)

        print(f"Total Spending for {start_date1.strftime('%B %Y')}: ${spending_period1:.2f}")
        print(f"Total Spending for {start_date2.strftime('%B %Y')}: ${spending_period2:.2f}")

        # Analyze spending trends by category
        period1_category_spending = defaultdict(float)
        period2_category_spending = defaultdict(float)

        for t in period1_transactions:
            normalized_category = t.category.lower()  # Normalize category names
            period1_category_spending[normalized_category] += t.amount
        for t in period2_transactions:
            normalized_category = t.category.lower()  # Normalize category names
            period2_category_spending[normalized_category] += t.amount

        print("\nSpending Trends by Category:")
        for category in period1_category_spending.keys() | period2_category_spending.keys():
            spending1 = period1_category_spending.get(category, 0)
            spending2 = period2_category_spending.get(category, 0)

            if spending1 == 0 and spending2 == 0:
                continue  # No spending in either period for this category

            if spending1 == 0:
                trend = "New spending in this category"
            elif spending2 == 0:
                trend = "No spending in this category for the second period"
            else:
                trend = ((spending2 - spending1) / spending1) * 100
                trend_sign = "+" if trend > 0 else ""
                trend = f"{trend_sign}{trend:.2f}%"

            print(f"{category.capitalize()}: {trend}")

    def add_transaction(self, transaction):
        """Add a transaction and save it to the file."""
        self.transactions.append(transaction)
        self.save_transactions()
        print("Transaction added successfully!")
        # Check if budget alerts are needed
        self.check_budget_alerts(transaction.category)
        if transaction.transaction_type == "Income":
            for goal_name, goal in self.savings_goals.items():
                if goal["saved_amount"] < goal["target_amount"]:
                    goal["saved_amount"] += transaction.amount
                    self.save_savings_goals()
                    print(f"Updated savings for goal '{goal_name}': ${goal['saved_amount']}")


    def calculate_summary(self):
        """Calculate total income, total expenses, and balance."""
        total_income = sum(t.amount for t in self.transactions if t.transaction_type == "Income")
        total_expense = sum(t.amount for t in self.transactions if t.transaction_type == "Expense")
        balance = total_income - total_expense
        return total_income, total_expense, balance

    def category_breakdown(self):
        """Provide a breakdown of spending and income by category."""
        breakdown = defaultdict(lambda: {"Income": 0, "Expense": 0})
        for t in self.transactions:
            breakdown[t.category][t.transaction_type] += t.amount
        return breakdown

    def show_transactions(self):
        """Display all transactions."""
        if not self.transactions:
            print("No transactions found.")
        else:
            print("\nTransaction History:")
            print(f"{'Date':<12} {'Category':<15} {'Type':<10} {'Amount':>8}")
            print("-" * 50)
            for t in self.transactions:
                print(f"{t.date:<12} {t.category:<15} {t.transaction_type:<10} ${t.amount:>8.2f}")
    def export_financial_report(self, filename="financial_report.txt"):
        """
        Generate a comprehensive financial report and export it to a text file.

        :param filename: Name of the file to export the report to (default: financial_report.txt)
        """
        try:
            with open(filename, "w") as report_file:
                # Financial Summary
                total_income, total_expense, balance = self.calculate_summary()
                report_file.write("=== FINANCIAL SUMMARY ===\n")
                report_file.write(f"Total Income:   ${total_income:.2f}\n")
                report_file.write(f"Total Expenses: ${total_expense:.2f}\n")
                report_file.write(f"Current Balance: ${balance:.2f}\n\n")

                # Category Breakdown
                report_file.write("=== CATEGORY BREAKDOWN ===\n")
                category_breakdown = self.category_breakdown()
                for category, values in category_breakdown.items():
                    report_file.write(f"{category}:\n")
                    report_file.write(f"  Income:   ${values['Income']:.2f}\n")
                    report_file.write(f"  Expense:  ${values['Expense']:.2f}\n")
                report_file.write("\n")

                # Budgets
                report_file.write("=== BUDGET STATUS ===\n")
                for category, budget_details in self.budgets.items():
                    utilization = self.track_budget_utilization(category)
                    report_file.write(f"{category} Budget:\n")
                    report_file.write(f"  Budget Amount: ${budget_details['amount']:.2f} ({budget_details['period']})\n")
                    report_file.write(f"  Utilization:   {utilization:.2f}%\n")
                report_file.write("\n")

                # Savings Goals
                report_file.write("=== SAVINGS GOALS ===\n")
                for goal_name, goal_details in self.savings_goals.items():
                    report_file.write(f"{goal_name}:\n")
                    report_file.write(f"  Target Amount: ${goal_details['target_amount']:.2f}\n")
                    report_file.write(f"  Months to Save: {goal_details['months_to_save']}\n")
                    report_file.write(f"  Current Savings: ${goal_details['saved_amount']:.2f}\n")
                    remaining = goal_details['target_amount'] - goal_details['saved_amount']
                    report_file.write(f"  Remaining to Save: ${remaining:.2f}\n")
                report_file.write("\n")

                # Recent Transactions (last 10)
                report_file.write("=== RECENT TRANSACTIONS ===\n")
                sorted_transactions = sorted(self.transactions, key=lambda x: x.date, reverse=True)
                for t in sorted_transactions[:10]:  # Last 10 transactions
                    report_file.write(f"{t.date} | {t.category} | {t.transaction_type}: ${t.amount:.2f}\n")

                # Spending Summary
                report_file.write("\n=== MONTHLY SPENDING SUMMARY ===\n")
                total_spent, category_spending = self.generate_spending_summary()
                for category, amount in category_spending.items():
                    report_file.write(f"{category}: ${amount:.2f}\n")

        except IOError as e:
            print(f"Error exporting report: {e}")
        else:
            print(f"Financial report exported successfully to {filename}")




    def get_balance(self):
        
        balance = 0
        for transaction in self.transactions:
            if transaction.transaction_type == "Income":
                balance += transaction.amount
            elif transaction.transaction_type == "Expense":
                balance -= transaction.amount
        return balance
    
    def get_total_income(self):
        total_income = sum(t.amount for t in self.transactions if t.transaction_type == "Income")
        return total_income
    
    def get_total_expenses(self):
        total_expenses = sum(t.amount for t in self.transactions if t.transaction_type == "Expense")
        return total_expenses