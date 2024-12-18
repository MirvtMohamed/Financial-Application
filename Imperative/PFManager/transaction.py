class Transaction:
    def __init__(self, date, category, amount, transaction_type):
        """
        Initialize a Transaction object.

        :param date: Date of the transaction (str, YYYY-MM-DD)
        :param category: Category of the transaction (e.g., Food, Rent)
        :param amount: Amount of the transaction (float)
        :param transaction_type: Type of transaction - 'Income' or 'Expense' (str)
        """
        self.date = date
        self.category = category
        self.amount = amount
        self.transaction_type = transaction_type

    def to_dict(self):
        """Convert the Transaction object into a dictionary for JSON saving."""
        return {
            "date": self.date,
            "category": self.category,
            "amount": self.amount,
            "transaction_type": self.transaction_type
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Transaction object from a dictionary."""
        return cls(
            data["date"],
            data["category"],
            data["amount"],
            data["transaction_type"]
        )
