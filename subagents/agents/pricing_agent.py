import re
import json
from graph.state import SubAgentResult
import logging

logger = logging.getLogger(__name__)


class PricingAgent:

    def __init__(self, menu_file_path: str = "data/menu_items.json"):
        self.menu_file_path = menu_file_path
        self.menu_data = self._load_menu()

    def execute(self, query: str, context: dict = None) -> SubAgentResult:
        try:
            condition, price = self._extract_price_condition(query)

            if condition is None:
                return self._build_response(
                    "Sorry, I couldn't understand the price condition.",
                    success=False,
                    error="Invalid price condition"
                )

            results = self._filter_items(condition, price)

            if not results:
                return self._build_response(
                    f"No items found for condition: {condition} ${price}",
                    success=True
                )

            formatted_items = [
                f"- {item['name']} (${item['price']})"
                for item in results
            ]

            output = f"Items matching your budget (condition: {condition} ${price}):\n\n"
            output += "\n".join(formatted_items)

            return self._build_response(output, success=True)

        except Exception as e:
            logger.error(f"Pricing agent error: {e}")
            return self._build_response(
                "",
                success=False,
                error=str(e)
            )

    def _build_response(self, output: str, success: bool = True, error: str = "") -> SubAgentResult:
        return SubAgentResult(
            agent_name="pricing_agent",
            output=output,
            success=success,
            citations=[self.menu_file_path] if success else [],
            retrieval_score=1.0 if success else 0.0,
            error=error
        )

    def _load_menu(self):
        try:
            with open(self.menu_file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading menu file: {e}")
            return []

    def _extract_price_condition(self, query: str):
        patterns = [
            (r"(?:below|under|less than|priced below|priced under|priced at less than)\s*\$?(\d+(?:\.\d{1,2})?)", "lt"),
            (r"(?:above|over|greater than|more than|priced over|priced above)\s*\$?(\d+(?:\.\d{1,2})?)", "gt"),
            (r"(?:equal to|exactly|priced at|=)\s*\$?(\d+(?:\.\d{1,2})?)", "eq"),
        ]

        for pattern, condition in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return condition, float(match.group(1))

        return None, None

    def _filter_items(self, condition: str, price: float):
        results = []

        for item in self.menu_data:
            if not item.get("available", True):
                continue

            item_price = item.get("price", 0)

            if condition == "lt" and item_price < price:
                results.append(item)
            elif condition == "gt" and item_price > price:
                results.append(item)
            elif condition == "eq" and item_price == price:
                results.append(item)

        return results