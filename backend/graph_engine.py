
import networkx as nx


def build_dependency_graph(analysis_results):
    """Build an accurate function-level dependency graph."""

    graph = nx.DiGraph()

    for result in analysis_results:
        if "error" in result:
            continue

        file_path = result["file"]
        graph.add_node(file_path, type="file")

        # Add function nodes.
        for function in result.get("functions", []):
            function_name = function["name"]
            function_id = f"{file_path}::{function_name}"

            graph.add_node(
                function_id,
                type="function",
                line=function["line"]
            )

            graph.add_edge(
                file_path,
                function_id,
                relation="contains"
            )

        # Add class nodes.
        for class_info in result.get("classes", []):
            class_name = class_info["name"]
            class_id = f"{file_path}::{class_name}"

            graph.add_node(
                class_id,
                type="class",
                line=class_info["line"]
            )

            graph.add_edge(
                file_path,
                class_id,
                relation="contains"
            )

    # Resolve direct calls within the same file.
    for result in analysis_results:
        if "error" in result:
            continue

        file_path = result["file"]

        function_names = {
            function["name"]
            for function in result.get("functions", [])
        }

        for function in result.get("functions", []):
            source = f"{file_path}::{function['name']}"

            for called_name in function.get("calls", []):
                if called_name not in function_names:
                    continue

                target = f"{file_path}::{called_name}"

                graph.add_edge(
                    source,
                    target,
                    relation="calls"
                )

    return graph


def graph_summary(graph):
    """Return a summary of the dependency graph."""

    return {
        "total_nodes": graph.number_of_nodes(),
        "total_edges": graph.number_of_edges(),
        "nodes": list(graph.nodes(data=True)),
        "edges": list(graph.edges(data=True))
    }
