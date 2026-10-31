from backend.analyzer import analyze_python_file

result = analyze_python_file("test_sample.py")

print("\n===== TRACELENS CODE ANALYSIS =====")
print(result)