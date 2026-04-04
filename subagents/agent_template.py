"""Template for creating new specialized subagents"""
from utils.llm_client import get_client
from graph.state import SubAgentResult
import logging

logger = logging.getLogger(__name__)


class TemplateAgent:
    """
    Template class for creating specialized subagents.
    
    This agent template demonstrates the structure for building
    custom agents that integrate with the main workflow.
    
    To create a new agent:
    1. Copy this file and rename to: agents/your_agent_name.py
    2. Replace "TemplateAgent" with your class name
    3. Implement the execute() method with your custom logic
    4. Register in subagents/router.py AVAILABLE_AGENTS dict
    """

    def __init__(self):
        """Initialize the agent with LLM client."""
        self.client = get_client()
        self.model = "gpt-4o-mini"

    def execute(self, query: str, context: dict = None) -> SubAgentResult:
        """
        Execute the agent on a query.
        
        Args:
            query: The user query or reformed query
            context: Optional context dict with state information
        
        Returns:
            SubAgentResult with output, citations, and metadata
        """
        try:
            # YOUR CUSTOM LOGIC HERE
            # Example: 
            # 1. Validate input
            # 2. Fetch data from external source (API, database, etc)
            # 3. Process and format results
            # 4. Generate response with LLM
            
            # Simple LLM call example:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a specialized food & beverage assistant.
                        
User Query: {query}

Provide a comprehensive, helpful response that:
1. Directly answers the question
2. Is accurate and well-reasoned
3. Includes relevant details and examples when appropriate
4. Is conversational but professional

Response:"""
                    }
                ]
            )

            output = response.choices[0].message.content.strip()
            
            # Return structured result
            return SubAgentResult(
                agent_name="template_agent",  # Change this to your agent name
                output=output,
                success=True,
                citations=[],  # Add citations if using RAG
                retrieval_score=1.0,  # Score from 0-1 based on confidence
                error=""
            )

        except Exception as e:
            logger.error(f"Template agent error: {e}")
            return SubAgentResult(
                agent_name="template_agent",
                output="",
                success=False,
                error=str(e)
            )

    def _extract_context(self, context: dict) -> str:
        """Extract relevant context from state."""
        if not context:
            return ""
        
        parts = []
        if "previous_results" in context:
            parts.append(f"Context from previous agents: {context['previous_results']}")
        if "intent" in context:
            parts.append(f"Query intent: {context['intent']}")
        
        return "\n".join(parts)

    def _fetch_external_data(self, query: str) -> dict:
        """
        Fetch data from external sources.
        
        Replace with your actual data fetching logic:
        - Database queries
        - API calls
        - File system access
        - Vector database searches
        """
        # Example structure
        return {
            "data": [],
            "source": "none",
            "success": False
        }

    def _format_results(self, data: dict) -> str:
        """Format fetched data into readable response."""
        if not data.get("success"):
            return "No data found."
        
        # Format your specific data here
        return str(data.get("data", ""))


# ============================================
# ADVANCED PATTERNS
# ============================================


class RAGEnabledAgent(TemplateAgent):
    """
    Template for agents that use Retrieval-Augmented Generation (RAG).
    Searches vector database before generating response.
    """

    def execute(self, query: str, context: dict = None) -> SubAgentResult:
        """Execute with RAG retrieval."""
        try:
            # 1. RETRIEVE from ChromaDB
            from rag.vector_store import VectorStore
            store = VectorStore()
            search_results = store.search(query, top_k=5)
            
            # 2. FORMAT context
            context_text = self._format_search_results(search_results)
            
            # 3. GENERATE response with context
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a food & beverage expert.
                        
Use this information to answer the question:

{context_text}

User Question: {query}

Provide a helpful response based on the information above."""
                    }
                ]
            )

            output = response.choices[0].message.content.strip()
            
            # 4. EXTRACT citations
            citations = [r.get("source", "") for r in search_results if r.get("source")]
            
            # 5. CALCULATE confidence score
            retrieval_score = search_results[0].get("score", 0.0) if search_results else 0.0
            
            return SubAgentResult(
                agent_name="rag_agent",
                output=output,
                success=True,
                citations=citations,
                retrieval_score=retrieval_score,
                error=""
            )
            
        except Exception as e:
            logger.error(f"RAG agent error: {e}")
            return SubAgentResult(
                agent_name="rag_agent",
                output="",
                success=False,
                error=str(e)
            )

    def _format_search_results(self, results: list) -> str:
        """Format search results as context."""
        lines = []
        for i, result in enumerate(results, 1):
            lines.append(f"\n[Source {i}]")
            lines.append(f"Content: {result.get('content', '')}")
            lines.append(f"Source: {result.get('source', 'Unknown')}")
        
        return "\n".join(lines)


class APIAgent(TemplateAgent):
    """
    Template for agents that call external APIs.
    """

    def __init__(self, api_key: str = None, api_endpoint: str = None):
        """Initialize with API credentials."""
        super().__init__()
        self.api_key = api_key
        self.api_endpoint = api_endpoint

    def execute(self, query: str, context: dict = None) -> SubAgentResult:
        """Execute with API call."""
        try:
            # 1. CALL external API
            import requests
            
            params = self._parse_query_for_api(query)
            response = requests.get(
                f"{self.api_endpoint}/search",
                params=params,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code}")
            
            api_data = response.json()
            
            # 2. PROCESS API response
            processed = self._process_api_response(api_data)
            
            # 3. GENERATE response
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Based on this data: {processed}
                        
Answer the user query: {query}"""
                    }
                ]
            )
            
            return SubAgentResult(
                agent_name="api_agent",
                output=response.choices[0].message.content.strip(),
                success=True,
                citations=[api_data.get("source", "")],
                retrieval_score=1.0,
                error=""
            )
            
        except Exception as e:
            logger.error(f"API agent error: {e}")
            return SubAgentResult(
                agent_name="api_agent",
                output="",
                success=False,
                error=str(e)
            )

    def _parse_query_for_api(self, query: str) -> dict:
        """Parse query into API parameters."""
        return {"q": query}

    def _process_api_response(self, data: dict) -> str:
        """Process and format API response."""
        return str(data)


class StateAwareAgent(TemplateAgent):
    """
    Template for agents that use workflow state.
    Can access previous agent results for multi-step reasoning.
    """

    def execute(self, query: str, context: dict = None) -> SubAgentResult:
        """Execute with access to workflow state."""
        try:
            context = context or {}
            
            # Access previous agent results
            previous_results = context.get("previous_results", [])
            combined_context = "\n".join(previous_results)
            
            # Build prompt with context
            prompt = f"""You have access to these previous results:

{combined_context}

Now answer this new query: {query}

Build on the previous context and provide additional insights or analysis."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return SubAgentResult(
                agent_name="state_aware_agent",
                output=response.content[0].text.strip(),
                success=True,
                error=""
            )
            
        except Exception as e:
            logger.error(f"State-aware agent error: {e}")
            return SubAgentResult(
                agent_name="state_aware_agent",
                output="",
                success=False,
                error=str(e)
            )
