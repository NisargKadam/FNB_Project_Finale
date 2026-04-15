"""Test your agent"""
#from FNB_Project_Finale.subagents.agents import preparation_time_agent
from subagents.agents.preparation_time_agent import PreparationTimeAgent

def test_agent():
    agent = PreparationTimeAgent()
    
    # Test case 1: Basic query
    result = agent.execute("What is the cooking /preparation time for making chicken dum biryani?")
    assert result.success, f"Agent failed: {result.error}"
    assert len(result.output) > 10, "Output too short"
    print("✅ Test 1 passed")
    
    # Test case 2: Another query
    result = agent.execute("How do I know the cooking steps for making chicken dum biryani?")
    assert result.success
    assert "preparation_time_agent" in result.agent_name
    print("✅ Test 2 passed")
    
    # Test case 3: Error handling
    result = agent.execute("")  # Empty query
    # Should either work or fail gracefully
    print("✅ Test 3 passed")

if __name__ == "__main__":
    test_agent()
    print("\n✅ All tests passed!")