import logging
import json
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class CuisineRAGAgent:

    def __init__(self, chroma_store, tool_registry):
        self.chroma = chroma_store
        self.tool_registry = tool_registry

    def retrieve(self, query: str):

        logger.info("====================================")
        logger.info(f"[RAG] QUERY: {query}")
        logger.info("====================================")

        # =========================
        # 1. VECTOR SEARCH
        # =========================
        vector_results = self.chroma.search(query)

        logger.info("[VECTOR RESULTS]")
        logger.info(f"Count: {len(vector_results)}")

        for i, item in enumerate(vector_results):
            logger.info(f"[VECTOR {i}] {item}")

        # =========================
        # 2. LOCAL FILE SEARCH
        # =========================
        local_results = self._local_search(query)

        logger.info("[LOCAL RESULTS]")
        logger.info(f"Count: {len(local_results)}")

        for i, item in enumerate(local_results):
            logger.info(
                f"[LOCAL {i}] "
                f"name={item.get('name')} | "
                f"cuisine={item.get('cuisine')} | "
                f"desc={item.get('description')}"
            )

        # =========================
        # 3. WEB SEARCH (DDGS MCP)
        # =========================
        web_results = self.tool_registry.call(
            "cuisine_search",
            {"query": query}
        )

        logger.info("[WEB RESULTS]")
        logger.info(f"Success: {web_results.get('success')}")

        if web_results.get("success"):
            for i, item in enumerate(web_results.get("data", [])):
                logger.info(
                    f"[WEB {i}] "
                    f"title={item.get('title')} | "
                    f"url={item.get('url')}"
                )
        else:
            logger.warning("[WEB] No results or failed search")

        # =========================
        # FINAL RETURN
        # =========================
        logger.info("====================================")
        logger.info("[RAG COMPLETE] Returning merged context")
        logger.info("====================================")

        return {
            "vector": vector_results,
            "local": local_results,
            "web": web_results
        }
        
    def _local_search(self, query: str):
        """
        Simple fallback local search (JSON / hardcoded / file-based)
        """   
        try:
            with open("data/menu_items.json", "r", encoding="utf-8") as f:
                data = json.load(f)

                query_lower = query.lower()

                results = []

                for item in data:
                    if (
                    query_lower in item.get("name", "").lower()
                    or query_lower in item.get("cuisine", "").lower()
                    or query_lower in item.get("description", "").lower()
                     ):
                        results.append(item)

                return results

        except Exception as e:
            logger.error(f"[LOCAL SEARCH ERROR] {e}")
            return []    