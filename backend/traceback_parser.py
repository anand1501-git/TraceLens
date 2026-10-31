import re


def parse_traceback(traceback_text):
    """Extract file, line number and error type from a traceback."""

    line_pattern = r'File "([^"]+)", line (\d+)'
    matches = re.findall(line_pattern, traceback_text)

    error_pattern = r'([A-Za-z_][A-Za-z0-9_]*Error|[A-Za-z_][A-Za-z0-9_]*Exception): (.+)'

    error_match = re.search(error_pattern, traceback_text)

    return {
        "frames": [
            {
                "file": file_path,
                "line": int(line_number)
            }
            for file_path, line_number in matches
        ],
        "error_type": error_match.group(1) if error_match else None,
        "error_message": error_match.group(2) if error_match else None
    }