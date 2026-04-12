"""Recipe Agent - Find and recommend recipes from the data store"""
from subagents.agent_template import TemplateAgent
from graph.state import SubAgentResult
import json
import os
import logging

logger = logging.getLogger(__name__)

DATA_FILE = os.path.join("data", "recipes.json")


class RecipeAgent(TemplateAgent):
    """
    Agent for: Finding and recommending recipes.

    This agent handles queries related to:
    - Step-by-step cooking instructions for a dish
    - Preparation and cook time for a recipe
    - Chef tips and tricks for a dish

    Example queries this agent should answer:
    - "How do I make Biryani?"
    - "What are the steps to cook Paneer Tikka Masala?"
    - "Give me the recipe for Chocolate Lava Cake"
    """

    def __init__(self):
        """Initialize the agent."""
        super().__init__()
        self.agent_name = "recipe_agent"

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

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
            # 1. Load recipes from JSON file
            recipes = self._load_recipes()

            # 2. Search for matching recipes
            matched = self._search_recipes(query, recipes)

            # 3. Format matched recipes as context for the LLM
            context_text = self._format_recipes(matched)

            # 4. Build prompt and call the LLM
            prompt = self._build_prompt(query, context_text)
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1200,
                messages=[{"role": "user", "content": prompt}],
            )

            output = response.choices[0].message.content.strip()

            # Build citation list from matched recipes
            citations = [r["dish_name"] for r in matched] if matched else []

            return SubAgentResult(
                agent_name=self.agent_name,
                output=output,
                success=True,
                citations=citations,
                retrieval_score=0.95 if matched else 0.5,
                error="",
            )

        except Exception as e:
            logger.error(f"Agent {self.agent_name} failed: {e}")
            return SubAgentResult(
                agent_name=self.agent_name,
                output="",
                success=False,
                error=str(e),
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_recipes(self) -> list:
        """Load all recipes from the JSON data file."""
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _search_recipes(self, query: str, recipes: list) -> list:
        """
        Return recipes whose dish_name appears (case-insensitive) in the query.
        Falls back to returning all recipes when no match is found so the LLM
        can still give a helpful general answer.
        """
        query_lower = query.lower()
        matched = [
            r for r in recipes
            if r.get("dish_name", "").lower() in query_lower
        ]
        return matched if matched else recipes  # fallback: send all recipes

    def _format_recipes(self, recipes: list) -> str:
        """Convert a list of recipe dicts into a readable text block."""
        lines = []
        for r in recipes:
            lines.append(f"### {r['dish_name']} (ID: {r['id']})")
            lines.append(f"- Serves: {r.get('serves', 'N/A')}")
            lines.append(
                f"- Prep time: {r.get('prep_time_minutes', 'N/A')} min | "
                f"Cook time: {r.get('cook_time_minutes', 'N/A')} min"
            )
            lines.append(f"- Difficulty: {r.get('difficulty', 'N/A')}")
            lines.append("**Steps:**")
            for i, step in enumerate(r.get("steps", []), 1):
                lines.append(f"  {i}. {step}")
            tips = r.get("chef_tips", [])
            if tips:
                lines.append("**Chef Tips:**")
                for tip in tips:
                    lines.append(f"  - {tip}")
            lines.append("")
        return "\n".join(lines)

    def _build_prompt(self, query: str, context_text: str) -> str:
        """Build the final LLM prompt."""
        return f"""You are a recipe assistant for a Food & Beverage AI system.

Below are the relevant recipes from our database:

{context_text}

User Query: {query}

Using only the recipe data above, provide a helpful, accurate response that:
1. Directly answers the question with clear step-by-step instructions
2. Mentions preparation and cooking times where relevant
3. Includes chef tips if they add value
4. Is professional but friendly
5. If the exact dish is not in the data, suggest the closest available recipe"""
