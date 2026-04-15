# Create test_manual.py:
from graph.main_graph import execute_query

# Test your agent with a query
response = execute_query("Your test query here?")

print("Response:", response)
print("Status:", response.get("status"))
print("Agents Used:", response.get("agents_used"))
print("Answer:", response.get("answer"))