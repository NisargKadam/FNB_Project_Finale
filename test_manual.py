"""Manual integration test for the recipe agent workflow."""
from graph.main_graph import execute_query


response = execute_query("How do I make Chicken Biryani?")

print("Response:", response)
print("Status:", response.get("status"))
print("Agents Used:", response.get("agents_used"))
print("Answer:", response.get("answer"))