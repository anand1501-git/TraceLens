import ast
from pathlib import Path


def get_dictionary_return(function_node):
    """Extract a literal dictionary returned by a function."""

    for node in ast.walk(function_node):
        if isinstance(node, ast.Return) and node.value is not None:
            try:
                value = ast.literal_eval(node.value)

                if isinstance(value, dict):
                    return value

            except (ValueError, TypeError, SyntaxError):
                continue

    return None


def trace_data_flow(file_path, source_function, consumer_function):
    """
    Trace dictionary values from a source function
    through a variable into a consumer function.
    """

    path = Path(file_path)

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))

    except (OSError, SyntaxError, UnicodeError) as error:
        return {"error": str(error)}

    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    if source_function not in functions:
        return {"error": f"Source function '{source_function}' not found"}

    if consumer_function not in functions:
        return {"error": f"Consumer function '{consumer_function}' not found"}

    dictionary = get_dictionary_return(functions[source_function])

    if dictionary is None:
        return {"error": "No literal dictionary return found"}

    consumer = functions[consumer_function]
    parameters = [
        arg.arg for arg in consumer.args.args
    ]

    results = []

    for caller in functions.values():

        variable_names = set()

        for node in ast.walk(caller):

            if not isinstance(node, ast.Assign):
                continue

            if not isinstance(node.value, ast.Call):
                continue

            called_name = (
                node.value.func.id
                if isinstance(node.value.func, ast.Name)
                else None
            )

            if called_name != source_function:
                continue

            for target in node.targets:
                if isinstance(target, ast.Name):
                    variable_names.add(target.id)

        if not variable_names:
            continue

        for node in ast.walk(caller):

            if not isinstance(node, ast.Call):
                continue

            called_name = (
                node.func.id
                if isinstance(node.func, ast.Name)
                else None
            )

            if called_name != consumer_function:
                continue

            for index, argument in enumerate(node.args):

                if index >= len(parameters):
                    continue

                if not isinstance(argument, ast.Subscript):
                    continue

                if not isinstance(argument.value, ast.Name):
                    continue

                variable = argument.value.id

                if variable not in variable_names:
                    continue

                key_node = argument.slice

                if not isinstance(key_node, ast.Constant):
                    continue

                key = key_node.value

                if key not in dictionary:
                    continue

                results.append({
                    "source_function": source_function,
                    "variable": variable,
                    "dictionary_key": key,
                    "value": dictionary[key],
                    "consumer_function": consumer_function,
                    "parameter": parameters[index],
                    "line": node.lineno,
                    "caller_function": caller.name,
                    "evidence": (
                        f"{variable}[{key!r}] receives "
                        f"{dictionary[key]!r} from "
                        f"{source_function}()"
                    )
                })

    return {
        "file": str(path),
        "source_function": source_function,
        "consumer_function": consumer_function,
        "data_flow": results
    }