class Budget:
    def __init__(self, category, amount, period):
        """
        Initialize a Budget object.

        :param category: The category for which the budget is set (e.g., Food, Rent).
        :param amount: The total amount allocated for this category.
        :param period: The time period for the budget ('monthly' or 'weekly').
        """
        self.category = category
        self.amount = amount
        self.period = period
        self.spent = 0  # Track how much has been spent in this category

    def add_expense(self, amount):
        """Add an expense to the category and update the spent amount."""
        self.spent += amount

    def remaining_budget(self):
        """Calculate remaining budget."""
        return self.amount - self.spent

    def is_nearing_limit(self, threshold=0.9):
        """Check if the budget is nearing the limit (default 90% utilization)."""
        return self.spent >= self.amount * threshold
