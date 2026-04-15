"""Preparation_time_agent - Cooking/preparation time estimates"""
from subagents.agent_template import TemplateAgent
from graph.state import SubAgentResult
from utils.llm_client import get_client
import logging
import json
import os

logger = logging.getLogger(__name__)


class PreparationTimeAgent(TemplateAgent):
    """
    Agent for: Cooking/preparation time estimates
    
    This agent handles queries related to:
    - [Main responsibility 1]
    - [Main responsibility 2]
    - [Main responsibility 3]
    
    Example queries this agent should answer:
    - "What is...?"
    - "How do I...?"
    """

    def __init__(self):
        """Initialize the agent."""
        super().__init__()
        self.agent_name = "preparation_time_agent"

    def execute(self, query: str, context: dict = None) -> SubAgentResult:
        """
        Execute the agent on a query.
        
        Args:
            query: The user question
            context: Optional context from workflow state
            
        Returns:
            SubAgentResult with answer and metadata
        """
        try:
            # Load recipes data from JSON file
            recipes_path = os.path.join(os.path.dirname(__file__), '../../data/recipes.json')
            
            with open(recipes_path, 'r', encoding='utf-8') as f:
                recipes = json.load(f)
            
            # Search for matching recipe in the query
            matching_recipe = None
            query_lower = query.lower()
            
            for recipe in recipes:
                if recipe['dish_name'].lower() in query_lower or query_lower in recipe['dish_name'].lower():
                    matching_recipe = recipe
                    break
            
            # Extract and calculate preparation time
            if matching_recipe:
                prep_time = matching_recipe.get('prep_time_minutes', 0)
                cook_time = matching_recipe.get('cook_time_minutes', 0)
                total_time = prep_time + cook_time
                dish_name = matching_recipe.get('dish_name', 'Unknown')
                difficulty = matching_recipe.get('difficulty', 'Not specified')
                serves = matching_recipe.get('serves', 'Unknown')
                
                output = f"""Recipe: {dish_name}
                
Preparation Time Estimate:
- Prep Time: {prep_time} minutes
- Cook Time: {cook_time} minutes
- Total Time: {total_time} minutes

Difficulty: {difficulty}
Serves: {serves} people

This recipe will take approximately {total_time} minutes from start to finish."""
            else:
                # If no recipe found, use LLM to provide general time estimation
                output = self.client.chat.completions.create(
                    model="gpt-4.1-mini",
                    max_tokens=1000,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""You are a preparation_time_agent assistant for a food & beverage system.

Your expertise: You are specialized in estimating the preparation time of recipes

User Query: {query}

Provide a helpful, accurate response that:
1. Directly answers the question about recipe preparation time
2. Includes breakdown of prep and cook time if applicable
3. Is professional but friendly
4. Is specific to food & beverage context"""
                        }
                    ]
                ).choices[0].message.content.strip()
            
            return SubAgentResult(
                agent_name=self.agent_name,
                output=output,
                success=True,
                citations=[],
                retrieval_score=0.95,
                error=""
            )

        except FileNotFoundError as e:
            logger.error(f"Recipes file not found: {e}")
            return SubAgentResult(
                agent_name=self.agent_name,
                output="",
                success=False,
                error=f"Recipe database not found: {str(e)}"
            )
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing recipes JSON: {e}")
            return SubAgentResult(
                agent_name=self.agent_name,
                output="",
                success=False,
                error=f"Invalid recipe data format: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Agent {self.agent_name} failed: {e}")
            return SubAgentResult(
                agent_name=self.agent_name,
                output="",
                success=False,
                error=str(e)
            )