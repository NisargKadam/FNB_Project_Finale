from ddgs import DDGS
import logging

logger = logging.getLogger(__name__)


class CuisineSearchTool:
    name = "cuisine_search"

    def run(self, query: str) -> dict:
        """
        MCP-style tool: fetch cuisine data from DDGS
        """

        logger.info(f"[MCP TOOL] cuisine_search called with query: {query}")

        try:
            results = []

            with DDGS() as ddgs:
                search_results = ddgs.text(
                    f"{query} cuisine food recipe",
                    max_results=5
                )

                for r in search_results:
                    results.append({
                        "title": r.get("title"),
                        "body": r.get("body"),
                        "url": r.get("href")
                    })

            return {
                "success": True,
                "data": results
            }

        except Exception as e:
            logger.exception("[MCP TOOL] cuisine_search failed")

            return {
                "success": False,
                "data": [],
                "error": str(e)
            }