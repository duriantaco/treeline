# This line is intentionally longer than 80 characters to test the style checker. It should be flagged.
def example_function():
    pass

def long_function():
    customer_name = "John Doe"
    date_range = ("2021-01-01", "2021-12-31")

    query = f"SELECT * FROM orders WHERE customer_name LIKE '%{customer_name}%' AND order_date BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    return query
