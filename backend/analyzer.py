
import ast
from pathlib import Path


class FunctionCallVisitor(ast.NodeVisitor):
    """Collect function calls belonging to one function."""

    def __init__(self):
        self.calls = []

    def visit_FunctionDef(self, node):
        return

    def visit_AsyncFunctionDef(self, node):
        return

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)

        elif isinstance(node.func, ast.Attribute):
            self.calls.append(node.func.attr)

        self.generic_visit(node)


class ValueAssignmentVisitor(ast.NodeVisitor):
    """Collect variable assignments and returned values."""

    def __init__(self):
        self.assignments = []
        self.returns = []

    def visit_FunctionDef(self, node):
        return

    def visit_AsyncFunctionDef(self, node):
        return

    def visit_Assign(self, node):
        value = self.get_value(node.value)

        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assignments.append({
                    "variable": target.id,
                    "value": value,
                    "line": node.lineno
                })

        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.assignments.append({
                "variable": node.target.id,
                "value": self.get_value(node.value),
                "line": node.lineno
            })

        self.generic_visit(node)

    def visit_Return(self, node):
        self.returns.append({
            "value": self.get_value(node.value),
            "line": node.lineno
        })

        self.generic_visit(node)

    def get_value(self, node):
        """Extract literal values, including dictionaries."""

        if node is None:
            return None

        try:
            return ast.literal_eval(node)

        except (ValueError, TypeError, SyntaxError):
            return None


def analyze_python_file(file_path):
    """Extract structural and value information from Python."""

    path = Path(file_path)

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))

    except (OSError, SyntaxError, UnicodeError) as error:
        return {
            "file": str(path),
            "error": str(error)
        }

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            call_visitor = FunctionCallVisitor()
            value_visitor = ValueAssignmentVisitor()

            for child in node.body:
                call_visitor.visit(child)
                value_visitor.visit(child)

            functions.append({
                "name": node.name,
                "line": node.lineno,
                "end_line": node.end_lineno,
                "calls": sorted(set(call_visitor.calls)),
                "assignments": value_visitor.assignments,
                "returns": value_visitor.returns
            })

        elif isinstance(node, ast.ClassDef):

            classes.append({
                "name": node.name,
                "line": node.lineno
            })

        elif isinstance(node, ast.Import):

            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")

    return {
        "file": str(path),
        "functions": functions,
        "classes": classes,
        "imports": sorted(set(imports))
    }


def analyze_project(project_path):
    """Analyze all Python files in a project."""

    root = Path(project_path)

    if not root.is_dir():
        raise NotADirectoryError(
            f"Invalid project directory: {root}"
        )

    results = []

    for file_path in sorted(root.rglob("*.py")):

        if any(
            part in {".venv", "__pycache__", ".git"}
            for part in file_path.parts
        ):
            continue

        results.append(analyze_python_file(file_path))

    return results
