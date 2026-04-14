"""Test your agent"""
from subagents.agents.menu_agent import MenuAgent

def test_agent():
    agent = MenuAgent()
    
    # Test case 1: Basic query
    response = agent.intelligent_query_handler("What is the menu available?")
    assert len(response) > 10, "Response too short"
    print("✅ Test 1 passed")
    
    # Test case 2: Another query
    response = agent.intelligent_query_handler("What are non veg items available?")
    assert len(response) > 10, "Response too short"
    assert "non-vegetarian" in response.lower() or "noodles" in response.lower()
    print("✅ Test 2 passed")
    
    # Test case 3: Error handling
    response = agent.intelligent_query_handler("")  # Empty query
    # Should either work or fail gracefully
    assert isinstance(response, str), "Response should be a string"
    print("✅ Test 3 passed")

if __name__ == "__main__":
    test_agent()
    print("\n✅ All tests passed!")