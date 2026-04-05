"""Subagent Router - Master orchestrator for 20+ specialized agents"""
from typing import Optional, Any
from graph.state import FnBState, SubAgentResult
from utils.llm_client import get_client, MODEL
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class SubAgentRouter:
    """
    Master router that coordinates execution of multiple specialized subagents.
    Supports parallel and sequential execution modes.
    
    Available Subagents (to be implemented):
    1. recipe_agent - Recipe search and recommendations
    2. nutrition_agent - Nutritional information queries
    3. menu_agent - Menu information and offerings
    4. recommendation_agent - Personalized recommendations
    5. dietary_agent - Dietary restrictions and alternatives
    6. allergen_agent - Allergen information
    7. pricing_agent - Price and cost information
    8. inventory_agent - Inventory and availability
    9. preparation_time_agent - Cooking/prep time estimates
    10. substitution_agent - Ingredient substitutions
    11. cuisine_agent - Cuisine type information
    12. seasonal_agent - Seasonal/local ingredients
    13. beverage_pairing_agent - Wine/drink pairings
    14. nutrition_calculator_agent - Calorie and macro calculations
    15. restaurant_info_agent - Restaurant details
    16. order_history_agent - Customer order history
    17. trending_agent - Trending dishes and cuisines
    18. comparison_agent - Compare multiple items
    19. sustainability_agent - Eco-friendly options
    20. feedback_agent - Customer reviews and ratings
    """

    AVAILABLE_AGENTS = {
        "recipe_agent": "Search and recommend recipes",
        "nutrition_agent": "Provide nutritional information",
        "menu_agent": "Find menu items and offerings",
        "recommendation_agent": "Personalized menu recommendations",
        "dietary_agent": "Handle dietary restrictions",
        "allergen_agent": "Allergen information and safety",
        "pricing_agent": "Price and cost queries",
        "inventory_agent": "Availability and inventory status",
        "preparation_time_agent": "Cooking/preparation times",
        "substitution_agent": "Ingredient substitutions",
        "cuisine_agent": "Cuisine type and origin info",
        "seasonal_agent": "Seasonal and local ingredients",
        "beverage_pairing_agent": "Wine and drink pairings",
        "nutrition_calculator_agent": "Detailed nutrition calculations",
        "restaurant_info_agent": "Restaurant information",
        "order_history_agent": "Customer order history",
        "trending_agent": "Trending and popular items",
        "comparison_agent": "Compare multiple items",
        "sustainability_agent": "Sustainability and eco-friendly options",
        "feedback_agent": "Reviews and customer feedback",
    }

    def __init__(self):
        self.client = get_client()
        self.max_workers = 5  # Parallel execution limit

    def process(self, state: FnBState) -> FnBState:
        """Route query to appropriate subagents."""
        if not state.agents_to_invoke:
            return state

        if state.execution_mode == "parallel":
            self._execute_parallel(state)
        else:
            self._execute_sequential(state)

        return state

    def _execute_sequential(self, state: FnBState) -> None:
        """Execute agents one at a time."""
        logger.info(f"Sequential execution for agents: {state.agents_to_invoke}")
        
        for agent_name in state.agents_to_invoke:
            result = self._execute_agent(state, agent_name)
            if result:
                state.subagent_results.append(result)

    def _execute_parallel(self, state: FnBState) -> None:
        """Execute agents in parallel (up to max_workers)."""
        logger.info(f"Parallel execution for agents: {state.agents_to_invoke}")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._execute_agent, state, agent_name): agent_name
                for agent_name in state.agents_to_invoke
            }
            
            for future in futures:
                try:
                    result = future.result(timeout=30)
                    if result:
                        state.subagent_results.append(result)
                except Exception as e:
                    agent_name = futures[future]
                    logger.error(f"Agent {agent_name} failed: {e}")
                    # Still add error result
                    state.subagent_results.append(
                        SubAgentResult(
                            agent_name=agent_name,
                            output="",
                            success=False,
                            error=str(e)
                        )
                    )

    def _execute_agent(self, state: FnBState, agent_name: str) -> Optional[SubAgentResult]:
        """Execute a single subagent."""
        if agent_name not in self.AVAILABLE_AGENTS:
            logger.warning(f"Unknown agent: {agent_name}")
            return SubAgentResult(
                agent_name=agent_name,
                output="",
                success=False,
                error=f"Agent {agent_name} not found"
            )

        try:
            agent_desc = self.AVAILABLE_AGENTS[agent_name]
            
            # Call the agent with the query
            response = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a specialized food & beverage agent.
Role: {agent_desc}

User Query: "{state.reformed_query}"

Provide a comprehensive response that:
1. Directly answers the question
2. Includes relevant details from your expertise area
3. Suggests related items if applicable
4. Notes any important caveats or disclaimers

Be conversational but professional."""
                    }
                ]
            )

            output = response.choices[0].message.content.strip()
            
            result = SubAgentResult(
                agent_name=agent_name,
                output=output,
                success=True,
                citations=[],  # Can be populated from RAG if needed
                retrieval_score=1.0  # Update after RAG evaluation
            )
            
            logger.info(f"Agent {agent_name} completed successfully")
            return result

        except Exception as e:
            logger.error(f"Agent {agent_name} execution failed: {e}")
            return SubAgentResult(
                agent_name=agent_name,
                output="",
                success=False,
                error=str(e)
            )

    def get_agent_list(self) -> dict:
        """Return list of available agents."""
        return self.AVAILABLE_AGENTS.copy()

    def register_agent(self, agent_name: str, description: str) -> None:
        """Register a new agent (for future expansion)."""
        self.AVAILABLE_AGENTS[agent_name] = description
        logger.info(f"Registered new agent: {agent_name}")
