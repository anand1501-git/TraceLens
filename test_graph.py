
from backend.analyzer import analyze_project
from backend.graph_engine import build_dependency_graph, graph_summary

results = analyze_project(".")

graph = build_dependency_graph(results)

print("\n===== TRACELENS DEPENDENCY GRAPH =====")
print(graph_summary(graph))
