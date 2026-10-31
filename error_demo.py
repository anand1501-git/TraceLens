def load_sales_data():
    """Load sales information."""
    return {
        "total_revenue": 5000,
        "items_sold": 0
    }


def calculate_average(total, count):
    """Calculate average revenue per item."""
    return total / count


def get_average_sale():
    """Get sales data and calculate the average."""
    sales = load_sales_data()

    average = calculate_average(
        sales["total_revenue"],
        sales["items_sold"]
    )

    return average


def generate_report():
    """Generate the final sales report."""
    average = get_average_sale()

    return f"Average sale value: ₹{average}"


def main():
    """Start the application."""
    print("Starting Sales Report Generator...")

    report = generate_report()

    print(report)


if __name__ == "__main__":
    main()