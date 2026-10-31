import unittest
from pathlib import Path

from backend.service import analyze_traceback


PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_TRACEBACK = """Traceback (most recent call last):
  File "error_demo.py", line 31, in <module>
    main()
  File "error_demo.py", line 27, in main
    report = generate_report()
  File "error_demo.py", line 21, in generate_report
    average = get_average_sale()
  File "error_demo.py", line 15, in get_average_sale
    average = calculate_average(
  File "error_demo.py", line 11, in calculate_average
    return total / count
ZeroDivisionError: division by zero
"""


class TestTracebackService(unittest.TestCase):

    def test_analyzes_matching_project_source(self):
        result = analyze_traceback(SAMPLE_TRACEBACK, PROJECT_ROOT)

        self.assertEqual(
            result["root_cause"]["failing_function"]["function"],
            "calculate_average"
        )
        self.assertEqual(
            result["root_cause"]["data_issue"]["parameter"],
            "count"
        )
        self.assertTrue(
            any(
                caller.endswith("error_demo.py::get_average_sale")
                for caller in result["root_cause"]["caller_chain"]
            )
        )

    def test_reports_when_traceback_does_not_match_project(self):
        result = analyze_traceback(
            'Traceback (most recent call last):\n'
            '  File "/tmp/external.py", line 1, in <module>\n'
            'ValueError: bad input',
            PROJECT_ROOT
        )

        self.assertEqual(result["root_cause"]["status"], "incomplete")
        self.assertEqual(
            result["root_cause"]["reason"],
            "Could not locate the failing function."
        )


if __name__ == "__main__":
    unittest.main()
