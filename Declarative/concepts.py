#from functools import reduce
import json


def manual_split(string, delimiter):
    def split_helper(s, delimiter, result):
        if not s:
            return result
        elif s[0] == delimiter:
            return split_helper(s[1:], delimiter, result + [''])
        else:
            return split_helper(s[1:], delimiter, result[:-1] + [result[-1] + s[0]])

    return split_helper(string, delimiter, [''])



def manual_strip(s, chars_to_remove=" \t\n\r"):
    def strip_helper(s, chars_to_remove, start, end):
        if start >= end:
            return s[start:end]
        if s[start] in chars_to_remove:
            return strip_helper(s, chars_to_remove, start + 1, end)
        if s[end - 1] in chars_to_remove:
            return strip_helper(s, chars_to_remove, start, end - 1)
        
        return s[start:end]

    return strip_helper(s, chars_to_remove, 0, manual_len(s))


def manual_sum(iterable):
    if not iterable:
        return 0
    return iterable[0] + manual_sum(iterable[1:])



def manual_sort(lst):
    if manual_len(lst) <= 1:
        return lst
    pivot = lst[0]
    def partition(lst, pivot):
        if not lst:
            return [], []
        head, *tail = lst
        lesser, greater = partition(tail, pivot)
        if head <= pivot:
            return lesser + [head], greater
        else:
            return lesser, greater + [head]
    
    lesser, greater = partition(lst[1:], pivot)
    
    return manual_sort(lesser) + [pivot] + manual_sort(greater)


def manual_len(input_data):
    def len_helper(input_data, count):
        if not input_data:
            return count
        return len_helper(input_data[1:], count + 1)

    return len_helper(input_data, 0)


def custom_map(func, iterable):
    iterable = tuple(iterable)
    if not iterable:
        return []
    return [func(iterable[0])] + custom_map(func, iterable[1:])

def custom_filter(func, iterable):
    iterable = tuple(iterable)
    if not iterable:
        return []
    if func(iterable[0]):
        return [iterable[0]] + custom_filter(func, iterable[1:])
    return custom_filter(func, iterable[1:])

def manual_parse_date(date_string):
    date_string = manual_strip(date_string)
    delimiter = '/' if '/' in date_string else '-'
    date_parts = manual_split(date_string, delimiter)
    return tuple(custom_map(int, date_parts[::-1])) if delimiter == '/' else tuple(custom_map(int, date_parts))

def group_by_month(transactions):
    def get_unique_dates(transactions, result=None):
        if result is None:
            result = set()
        if not transactions:
            return result
        date = manual_parse_date(transactions[0]['date'])[:2]
        return get_unique_dates(transactions[1:], result | {date})

    unique_dates = get_unique_dates(transactions)

    
    def category_total(transactions, year, month, category, index=0, total=0):
        if index >= manual_len(transactions):
            return total
        t = transactions[index]
        if manual_parse_date(t['date'])[:2] == (year, month) and t['category'] == category:
            amount = t['amount'] if t['type'] == 'expense' else -t['amount']
            return category_total(transactions, year, month, category, index + 1, total + amount)
        return category_total(transactions, year, month, category, index + 1, total)

    def construct_month_data(transactions, year, month):         #containing totals for each category.
        categories = get_unique_categories(transactions, year, month)
        return dict(custom_map(lambda category: (category, category_total(transactions, year, month, category)), categories))

    def get_unique_categories(transactions, year, month, index=0, categories=None):
        if categories is None:
            categories = set()
        if index >= manual_len(transactions):
            return categories
        t = transactions[index]
        if manual_parse_date(t['date'])[:2] == (year, month):
            categories.add(t['category'])
        return get_unique_categories(transactions, year, month, index + 1, categories)

    def construct_result(unique_dates, transactions, index=0, result=None):
        if result is None:
            result = {}
        if index >= manual_len(unique_dates):
            return result
        year, month = unique_dates[index]
        result[(year, month)] = construct_month_data(transactions, year, month)
        return construct_result(unique_dates, transactions, index + 1, result)

    return construct_result(tuple(unique_dates), transactions)


def compare_spending(current, previous):
    return (current - previous) / previous * 100 if previous else 0


def create_insights_for_month(month, current_month_spending, spending_trends):      # generates insights for a given month
    total_spent, category_trends, total_trend = spending_trends
    current_month_insights = {
        'Total': f"Total spending in {month[0]}-{month[1]:02d}: {total_spent:.2f}",
        **category_trends,
        'Total Trend': total_trend
    }
    return (month, current_month_insights)

def generate_monthly_insights(grouped_transactions, previous_month_spending=None, months=None, insights=None):  # comparing the insights of each category with the month before
    if months is None:
        months = manual_sort(tuple(grouped_transactions.keys()))  
    if insights is None:
        insights = []
    if not months:
        return insights
    
    month = months[0]
    previous_month_spending = previous_month_spending or {}
    spending_trends = calculate_spending_trends(grouped_transactions[month], previous_month_spending)

    current_month_insights = create_insights_for_month(month, grouped_transactions[month], spending_trends)

    return generate_monthly_insights(
        grouped_transactions,
        grouped_transactions[month], 
        months[1:],  
        insights + [current_month_insights]  
    )

def calculate_spending_trends(current_month_spending, previous_month_spending):
    total_spent = manual_sum(tuple(current_month_spending.values()))  # Total spending for the current month

    def category_trend(category, current_spent):
        previous_spent = previous_month_spending.get(category, 0)
        trend = compare_spending(current_spent, previous_spent)
        return f"Spending on {category} changed by {round(trend, 2)}%." if trend != 0 else None

    def process_categories(categories, result=None):
        if not categories:
            return result if result else {}
        category, current_spent = categories[0]
        trend = category_trend(category, current_spent)
        if trend:
            result = result or {}
            result[category] = trend
        return process_categories(categories[1:], result)

    category_trends = process_categories(list(current_month_spending.items()))

    previous_total_spent = manual_sum(tuple(previous_month_spending.values()))
    total_trend = compare_spending(total_spent, previous_total_spent)
    total_trend_message = f"Total spending {'increased' if total_trend > 0 else 'decreased' if total_trend < 0 else 'remained the same'} by {round(total_trend, 2)}%."

    return total_spent, category_trends, total_trend_message


def display_monthly_insights(insights):
    def format_month_insight(month, category_insights):
        month_str = f"\n--- Insights for {month[0]}-{month[1]:02d} ---"
        category_str = "\n".join(category_insights.values())
        return f"{month_str}\n{category_str}\n"

    insights_display = custom_map(
        lambda item: format_month_insight(item[0], item[1]), 
        insights
    )
    
    print("\n".join(insights_display))



def add_transaction(transactions, new_transaction=None, file_path=None, file_type=None):
    return tuple(transactions) + tuple(import_file(file_path, file_type) if file_path and file_type else (new_transaction,) if new_transaction else ())


def set_budget(budgets, category, amount):
    new_budgets = dict(budgets) 
    new_budgets[category] = amount  
    return new_budgets


def track_budget(transactions, budgets, threshold=0.9):
    def accumulate_spending(transactions, index=0, result=None):
        if result is None:
            result = {}
        if index >= manual_len(transactions):
            return result
        t = transactions[index]
        new_amount = result.get(t['category'], 0) + t['amount']
        return accumulate_spending(transactions, index + 1, {**result, t['category']: new_amount})
    
    spending_by_category = accumulate_spending(transactions)

    filter_spending = custom_filter(
        lambda item: item[0] in budgets and item[1] >= budgets[item[0]] * threshold,
        spending_by_category.items()
    )

    result = custom_map(
        lambda item: (
            item[0],
            (item[1] - budgets[item[0]] if item[1] > budgets[item[0]] else 'nearing limit')
        ),
        filter_spending
    )

    return dict(result)



def set_savings_goal(savings_goals, goal_name, target_amount, months):
    monthly_savings = calculate_monthly_savings(target_amount, months)
    new_goal = {
        'goal_name': goal_name,
        'target_amount': target_amount,
        'months': months,
        'progress': 0,
        'monthly_savings': monthly_savings
    }
    print(f"For your goal '{goal_name}', you need to save ${monthly_savings} per month.")
    return savings_goals + [new_goal]


def calculate_monthly_savings(target_amount, months):
    return target_amount // months


def recommend_savings(savings_goals):
    return tuple(
        custom_map(
            lambda goal: (
                {'goal_name': goal['goal_name'], 
                 'monthly_savings': calculate_monthly_savings(goal['target_amount'], goal['months'])}
            ),
            savings_goals
        )
    )



def export_csv(transactions, file_path):
    try:
        def format_transaction(t):
            return f"{manual_strip(t['date'])},{t['amount']},{manual_strip(t['category'])},{manual_strip(t['type'])}\n"

        lines = tuple(custom_map(format_transaction, transactions))  
        with open(file_path, 'w') as file:
            file.write('date,amount,category,type\n')  
            file.writelines(lines)  
        
        print(f"Transactions successfully exported to {file_path}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")


def import_file(file_path, file_type): 
    if file_type.lower() == 'csv':
        return import_csv(file_path)
    elif file_type.lower() == 'json':
        return import_json(file_path) 
    print("Unsupported file type. Please use 'csv' or 'json'.")
    return ()


def import_csv(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
            def process_line(line):
                values = manual_split(manual_strip(line, '\n'), ',')
                if manual_len(values) == manual_len(manual_split(manual_strip(lines[0], '\n'), ',')) and values[1].strip().isdigit():
                    return {
                        'date': values[0], 
                        'amount': int(values[1]) if values[1].strip() else 0, 
                        'category': values[2], 
                        'type': values[3]
                    }
                return None
            transactions = tuple(filter(None, custom_map(process_line, lines[1:])))
            print(f"Successfully imported {manual_len(transactions)} transactions.")
            return transactions

    except FileNotFoundError:
        print("CSV file not found. Please check the file path.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return ()


def import_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if isinstance(data, list):
                transactions = tuple(data) 
                print(f"Transactions imported successfully. Now you have {manual_len(transactions)} transactions.")
                return transactions
            print("Invalid JSON format: The data is not a list of transactions.")
    except FileNotFoundError:
        print("JSON file not found. Please check the file path.")
    except json.JSONDecodeError:
        print("Error decoding JSON file. Please ensure the file is correctly formatted.")
    except Exception as e:
        print(f"Error reading JSON file: {e}")
    return ()


def export_report(transactions, budgets, savings_goals, file_path, threshold=0.9):
    try:
        def write_section(file, header, data, format_function):
            file.write(header + "\n")
            file.write("-" * 40 + "\n")
            data = data or ("No data available.",)  
            tuple(custom_map(lambda item: format_function(file, item), data))
            file.write("\n")

        def write_transaction(file, transaction):
            file.write(f"Date: {transaction['date']}, "
                       f"Category: {transaction['category']}, "
                       f"Type: {transaction['type']}, "
                       f"Amount: {transaction['amount']}\n")
        
        def write_budget_and_alerts(file, budgets, transactions):
            file.write("2. Budget and Alerts\n")
            file.write("-" * 40 + "\n")
            if not budgets:
                file.write("No budget set.\n")
            else:
                tuple(custom_map(lambda item: file.write(f"Category: {item[0]}, Budget Limit: {item[1]}\n"), budgets.items()))
                alerts = track_budget(transactions, budgets, threshold)
                if alerts:
                    file.write("\nAlerts:\n")
                    tuple(custom_map(lambda item: file.write(f"- Alert: Spending in '{item[0]}' exceeded the budget by {item[1]}\n"), alerts.items()))
                else:
                    file.write("\nNo alerts triggered.\n")
            file.write("\n")
        
        with open(file_path, 'w') as file:
            file.write("Financial Report\n")
            file.write("=" * 40 + "\n\n")

            write_section(file, "1. Transactions Overview", transactions, write_transaction)
            write_budget_and_alerts(file, budgets, transactions)
            
            write_section(file, "3. Savings Goals and Recommendations", savings_goals, lambda file, goal: file.write(
                f"Goal Name: {goal['goal_name']}\n"
                f"Target Amount: ${goal['target_amount']}\n"
                f"Timeframe: {goal['months']} months\n"
                f"Monthly Savings Needed: ${goal['monthly_savings']}\n"
                "-".ljust(40, '-') + "\n"
            ))


            file.write("4. Monthly Insights\n")
            file.write("-" * 40 + "\n")
            if transactions:
                grouped_transactions = group_by_month(transactions)
                monthly_insights = generate_monthly_insights(grouped_transactions)
                if monthly_insights:
                    tuple(custom_map(lambda month: (
                        file.write(f"--- Insights for {month[0][0]}-{month[0][1]:02d} ---\n"),
                        tuple(custom_map(lambda item: file.write(f"{item[0]}: {item[1]}\n"), month[1].items())),
                        file.write("\n")
                    ), monthly_insights))
                else:
                    file.write("No monthly insights available.\n")

            file.write("\nReport generated successfully.\n")
    except Exception as e:
        print(f"An error occurred while generating the report: {e}")


def main():
    transactions = []
    budgets = {}
    savings_goals = []

    def display_menu():
        print("\n--- Personal Finance Application ---")
        print("1. Record a Transaction (Income/Expense)")
        print("2. View All Transactions")
        print("3. Set Budget")
        print("4. Set Savings Goal")
        print("5. Track Spending Against Budget")
        print("6. View Spending Trends & Insights")
        print("7. Export Transactions csv")
        print("8. Import Transactions (CSV/JSON)")
        print("9. Write Report to Word")
        print("10. Exit")

    def process_choice(choice):
        nonlocal transactions, budgets, savings_goals

        if choice == '1':
            date = input("Enter the transaction date (e.g., 2024-12-13): ")
            amount = int(input("Enter the transaction amount: "))
            category = input("Enter the category (e.g., Food, Rent): ")
            transaction_type = input("Enter the transaction type (income/expense): ").lower()

            new_transaction = {
                "date": date,
                "amount": amount,
                "category": category,
                "type": transaction_type
            }
            transactions = add_transaction(transactions, new_transaction=new_transaction)
            print(f"Transaction added: {new_transaction}")

        elif choice == '2':
            print("\n--- All Transactions ---")
            if transactions:
                transaction_strings = custom_map(
                    lambda t: f"Date: {t['date']}, Amount: {t['amount']}, Category: {t['category']}, Type: {t['type']}", 
                    transactions
                )
                print("\n".join(transaction_strings))
            else:
                print("No transactions available.")

        elif choice == '3':
            category = input("Enter the category for the budget (e.g., Food, Rent): ")
            amount = int(input(f"Enter the budget amount for {category}: "))
            budgets = set_budget(budgets, category, amount)
            print(f"Budget set for {category}: ${amount}")

        elif choice == '4':
            goal_name = input("Enter the savings goal name (e.g., Vacation Fund): ")
            target_amount = int(input("Enter the target amount for the goal: "))
            months = int(input("Enter the number of months to reach the goal: "))
            savings_goals = set_savings_goal(savings_goals, goal_name, target_amount, months)
            print(f"Savings goal set: {goal_name}, Target: ${target_amount}, Months: {months}")

        elif choice == '5':
            alerts = track_budget(transactions, budgets)
            if alerts:
                print("\n--- Budget Alerts ---")
                alert_messages = custom_map(
                    lambda item: (
                        f"Warning: You're nearing the budget for {item[0]}."
                        if item[1] == 'nearing limit'
                        else f"Alert: You've exceeded the budget for {item[0]} by ${abs(item[1])}."
                    ),
                    alerts.items()
                )
                print("\n".join(alert_messages))
            else:
                print("No spending alerts.")

        elif choice == '6':
            grouped_transactions = group_by_month(transactions)
            insights = generate_monthly_insights(grouped_transactions)
            display_monthly_insights(insights)

        elif choice == '7':
            file_type = input("Enter the file type to export 'csv':").lower()
            file_path = input("Enter the file path (including filename): ")

            if file_type == 'csv':
                export_csv(transactions, file_path)
            else:
                print("Invalid file type. Please choose 'csv'.")

        elif choice == '8':
            import_choice = input("Choose import format (csv/json): ").lower()
            file_path = input("Enter the file path to import the transactions from: ")

            if import_choice in ['csv', 'json']:
                transactions = add_transaction(transactions, file_path=file_path, file_type=import_choice)
                print(f"Transactions imported successfully from {file_path}. Now you have {manual_len(transactions)} transactions.")
            else:
                print("Invalid choice. Please choose 'csv' or 'json'.")

        elif choice == '9':
            file_path = input("Enter the file path to save the report: ")
            export_report(transactions, budgets, savings_goals, file_path)

        elif choice == '10':
            print("Exiting the application...")

        else:
            print("Invalid choice. Please select a number between 1 and 9.")

        if choice != '10':
            display_menu()
            next_choice = input("Please select an option (1-10): ")
            process_choice(next_choice)

    display_menu()
    choice = input("Please select an option (1-10): ")
    process_choice(choice)


if __name__ == "__main__":
    main()



# C:\\Users\\hp\\Downloads\\tran.csv
# C:\\Users\\hp\\Downloads\\tran.json
# C:\\Users\\hp\\Downloads\\tran.txt