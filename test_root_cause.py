import unittest

from backend.analyzer import analyze_project
from backend.graph_engine import build_dependency_graph
from backend.traceback_parser import parse_traceback
from backend.data_flow import trace_data_flow
from backend.root_cause import build_root_cause_report


SAMPLE_TRACEBACK = """Traceback (most recent call last):
  File "error_demo.py", line 43, in <module>
    main()
  File "error_demo.py", line 37, in main
    report = generate_report()
  File "error_demo.py", line 28, in generate_report
    average = get_average_sale()
  File "error_demo.py", line 18, in get_average_sale
    average = calculate_average(
  File "error_demo.py", line 11, in calculate_average
    return total / count
ZeroDivisionError: division by zero
"""


class TestRootCause(unittest.TestCase):

    def test_combined_root_cause_report(self):

        results = analyze_project(".")
        graph = build_dependency_graph(results)

        traceback_data = parse_traceback(SAMPLE_TRACEBACK)

        flow = trace_data_flow(
            "error_demo.py",
            "load_sales_data",
            "calculate_average"
        )

        report = build_root_cause_report(
            traceback_data,
            results,
            graph,
            flow
        )

        self.assertEqual(report["status"], "analyzed")
        self.assertEqual(report["error_type"], "ZeroDivisionError")

        self.assertEqual(
            report["failing_function"]["function"],
            "calculate_average"
        )

        self.assertIsNotNone(report["data_issue"])
        self.assertEqual(report["data_issue"]["parameter"], "count")
        self.assertEqual(report["data_issue"]["value"], 0)

        self.assertIn(
            "error_demo.py::get_average_sale",
            report["caller_chain"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)