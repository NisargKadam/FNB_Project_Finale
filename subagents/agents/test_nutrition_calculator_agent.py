"""Test your agent"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from subagents.agents.nutrition_calculator_agent import NutritionCalculatorAgent

def test_agent():
    agent = NutritionCalculatorAgent()

    result = agent.execute("What is calories for Dal Makhani?")
    assert result.success, f"Agent failed: {result.error}"
    assert "calories" in result.output.lower()
    assert result.agent_name == "nutrition_calculator_agent"
    print("✅ Test 1 passed")

    result = agent.execute("How many calories are in Beef Tenderloin Steak?")
    assert result.success, f"Agent failed: {result.error}"
    assert "calories" in result.output.lower()
    assert result.agent_name == "nutrition_calculator_agent"
    print("✅ Test 2 passed")

    result = agent.execute("")
    assert not result.success
    assert "no food item" in result.output.lower()
    print("✅ Test 3 passed")

if __name__ == "__main__":
    test_agent()
    print("\n✅ All tests passed!")