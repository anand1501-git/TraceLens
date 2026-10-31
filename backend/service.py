import ast
from pathlib import Path

from backend.analyzer import analyze_project
from backend.data_flow import trace_data_flow
from backend.graph_engine import build_dependency_graph
from backend.root_cause import build_root_cause_report
from backend.traceback_parser import parse_traceback


def _match_project_file(frame_path, project_root, project_files):
    candidate = Path(frame_path)

    if candidate.is_absolute():
        resolved = candidate.resolve()
        return resolved if resolved in project_files else None

    resolved = (project_root / candidate).resolve()
    if resolved in project_files:
        return resolved

    basename_matches = [
        path for path in project_files if path.name == candidate.name
    ]
    return basename_matches[0] if len(basename_matches) == 1 else None


def _dictionary_return_functions(file_path):
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeError):
        return []

    functions = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        for child in ast.walk(node):
            if not isinstance(child, ast.Return) or child.value is None:
                continue
            try:
                value = ast.literal_eval(child.value)
            except (ValueError, TypeError, SyntaxError):
                continue
            if isinstance(value, dict):
                functions.append(node.name)
                break

    return functions


def analyze_traceback(traceback_text, project_path):
    project_root = Path(project_path).resolve()
    analysis_results = analyze_project(project_root)
    project_files = {
        Path(result["file"]).resolve()
        for result in analysis_results
        if "error" not in result
    }

    parsed_traceback = parse_traceback(traceback_text)
    matched_frames = []
    for frame in parsed_traceback["frames"]:
        project_file = _match_project_file(
            frame["file"], project_root, project_files
        )
        if project_file is not None:
            matched_frames.append({
                **frame,
                "file": str(project_file)
            })

    scoped_traceback = {
        **parsed_traceback,
        "frames": matched_frames
    }
    graph = build_dependency_graph(analysis_results)

    data_flow = {}
    if matched_frames:
        failing_file = Path(matched_frames[-1]["file"])
        failing_result = next(
            result for result in analysis_results
            if Path(result["file"]).resolve() == failing_file
        )
        failing_function = next(
            (
                function["name"]
                for function in failing_result.get("functions", [])
                if function["line"] <= matched_frames[-1]["line"]
                <= function["end_line"]
            ),
            None
        )

        if failing_function:
            for source_function in _dictionary_return_functions(failing_file):
                candidate_flow = trace_data_flow(
                    failing_file,
                    source_function,
                    failing_function
                )
                if candidate_flow.get("data_flow"):
                    data_flow = candidate_flow
                    break

    report = build_root_cause_report(
        scoped_traceback,
        analysis_results,
        graph,
        data_flow
    )
    return {
        "traceback": parsed_traceback,
        "root_cause": report
    }
