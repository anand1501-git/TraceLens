import unittest

from backend.data_flow import trace_data_flow


class TestDataFlow(unittest.TestCase):

    def test_dictionary_values_reach_function_parameters(self):

        result = trace_data_flow(
            "error_demo.py",
            "load_sales_data",
            "calculate_average"
        )

        self.assertNotIn("error", result)

        data_flow = result["data_flow"]

        self.assertEqual(len(data_flow), 2)

        revenue = next(
            item for item in data_flow
            if item["dictionary_key"] == "total_revenue"
        )

        count = next(
            item for item in data_flow
            if item["dictionary_key"] == "items_sold"
        )

        self.assertEqual(revenue["value"], 5000)
        self.assertEqual(revenue["parameter"], "total")

        self.assertEqual(count["value"], 0)
        self.assertEqual(count["parameter"], "count")


if __name__ == "__main__":
    unittest.main()