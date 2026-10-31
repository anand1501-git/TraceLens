def locate_error_function(traceback_data, analysis_results):
    """Find the function containing the failing traceback line."""

    if not traceback_data["frames"]:
        return None

    error_frame = traceback_data["frames"][-1]
    error_file = error_frame["file"]
    error_line = error_frame["line"]

    for result in analysis_results:
        if "error" in result or result["file"] != error_file:
            continue

        for function in result.get("functions", []):
            if function["line"] <= error_line <= function["end_line"]:
                return {
                    "file": error_file,
                    "function": function["name"],
                    "error_line": error_line,
                    "function_start": function["line"],
                    "function_end": function["end_line"]
                }

    return None


def trace_callers(graph, error_function):
    """Trace callers backwards from the failing function."""

    if not error_function:
        return []

    target = (
        f"{error_function['file']}::"
        f"{error_function['function']}"
    )

    if target not in graph:
        return []

    caller_chain = []
    visited = set()
    stack = [target]

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.add(current)

        callers = [
            node for node in graph.predecessors(current)
            if graph.edges[node, current].get("relation") == "calls"
        ]

        for caller in sorted(callers):
            caller_chain.append(caller)
            stack.append(caller)

    return caller_chain


def identify_data_issue(data_flow):
    """Identify suspicious values in traced data."""

    if not data_flow:
        return None

    for item in data_flow:
        value = item.get("value")
        parameter = item.get("parameter")

        if value == 0 and parameter in {
            "count", "divisor", "denominator"
        }:
            return {
                "type": "zero_value",
                "parameter": parameter,
                "value": value,
                "source_function": item["source_function"],
                "dictionary_key": item["dictionary_key"],
                "consumer_function": item["consumer_function"],
                "evidence": item["evidence"],
                "explanation": (
                    f"The parameter '{parameter}' receives 0. "
                    "This is consistent with a division-by-zero error."
                )
            }

    return None


def build_root_cause_report(
    traceback_data,
    analysis_results,
    graph,
    data_flow
):
    """Combine traceback, caller and data-flow evidence."""

    error_function = locate_error_function(
        traceback_data,
        analysis_results
    )

    if error_function is None:
        return {
            "status": "incomplete",
            "reason": "Could not locate the failing function."
        }

    caller_chain = trace_callers(graph, error_function)

    data_issue = identify_data_issue(
        data_flow.get("data_flow", [])
    )

    return {
        "status": "analyzed",
        "error_type": traceback_data.get("error_type"),
        "error_message": traceback_data.get("error_message"),
        "failing_function": error_function,
        "caller_chain": caller_chain,
        "data_issue": data_issue
    }