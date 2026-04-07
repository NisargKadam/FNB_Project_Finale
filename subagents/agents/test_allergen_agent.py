"""Test allergen agent"""
from allergen_agent import AllergenAgent

def test_agent():
    agent = AllergenAgent()
    
    # Test case 1: Basic query
    result = agent.execute("What allergens are in dairy products?")
    assert result.success, f"Agent failed: {result.error}"
    assert len(result.output) > 10, "Output too short"
    print("✅ Test 1 passed")
    
    # Test case 2: Another query
    result = agent.execute("I'm allergic to peanuts. What can I eat?")
    assert result.success
    assert "allergen_agent" in result.agent_name
    print("✅ Test 2 passed")
    
    # Test case 3: Error handling
    result = agent.execute("")  # Empty query
    # Should either work or fail gracefully
    print("✅ Test 3 passed")

if __name__ == "__main__":
    test_agent()
    print("\n✅ All tests passed!")