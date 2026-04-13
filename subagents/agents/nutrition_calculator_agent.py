import json
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from graph.state import SubAgentResult

class NutritionCalculatorAgent:

    def execute(self, query: str, context: dict = None) -> SubAgentResult:
        if context is None:
            context = {}

        if not isinstance(query, str) or not query.strip():
            return SubAgentResult(
                agent_name="nutrition_calculator_agent",
                output="No food item provided. Please ask for calories for a specific food.",
                success=False,
                data={}
            )

        match = re.search(r'(?:calor(?:y|ies)\s+(?:for|in)\s+)(.+)', query, re.IGNORECASE)
        food_item = match.group(1).strip() if match else query.strip()
        food_item = re.sub(r'[?\.!]+$', '', food_item).strip()
        food_item_lower = food_item.lower()

        json_path = Path(__file__).resolve().parents[2] / "data" / "nutritional_info.json"
        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as e:
            return SubAgentResult(
                agent_name="nutrition_calculator_agent",
                output=f"Nutrition data file not found: {json_path}",
                success=False,
                error=str(e),
                data={}
            )

        found_item = None
        for item in data:
            name = item.get("name", "")
            description = item.get("description", "")
            name_lower = name.lower()
            description_lower = description.lower()
            if (
                food_item_lower == name_lower
                or food_item_lower in name_lower
                or name_lower in food_item_lower
                or food_item_lower in description_lower
                or description_lower in food_item_lower
            ):
                found_item = item
                break

        if found_item is None:
            response_text = f"No nutrition entry found for '{food_item}'."
            success = False
        else:
            calories = found_item.get("calories")
            if calories is None:
                response_text = f"Found '{found_item.get('name', food_item)}' but no calorie value is available."
                success = False
            else:
                response_text = f"{found_item.get('name', food_item)} contains {calories} calories."
                success = True

        return SubAgentResult(
            agent_name="nutrition_calculator_agent",
            output=response_text,
            success=success,
            data={"food_item": found_item}
        )