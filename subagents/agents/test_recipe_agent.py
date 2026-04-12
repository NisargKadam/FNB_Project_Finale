"""Unit tests for the recipe agent."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from subagents.agents.recipe_agent import RecipeAgent


def test_agent():
    agent = RecipeAgent()

    result = agent.execute("How do I make Chicken Biryani?")
    assert result.success, f"Agent failed: {result.error}"
    assert len(result.output) > 10, "Output too short"
    print("Test 1 passed")

    result = agent.execute("What are the steps to cook Paneer Tikka Masala?")
    assert result.success, f"Agent failed: {result.error}"
    assert "recipe_agent" in result.agent_name
    print("Test 2 passed")

    result = agent.execute("")
    assert result.agent_name == "recipe_agent"
    print("Test 3 passed")


if __name__ == "__main__":
    test_agent()
    print("\nAll tests passed!")