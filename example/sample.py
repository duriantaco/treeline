class Calculator:
    """A simple calculator class."""

    def __init__(self):
        self.value = 0

    def add(self, x: int, y: int) -> int:
        """Add two numbers."""
        return x + y

    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers."""
        return x * y


def main():
    calc = Calculator()
    result = calc.add(5, 3)
    print(f"5 + 3 = {result}")


if __name__ == "__main__":
    main()