"""Allergen Agent - Provides allergen information and safety recommendations"""
from subagents.agent_template import TemplateAgent
from graph.state import SubAgentResult
from utils.llm_client import get_client, MODEL
import logging

logger = logging.getLogger(__name__)


class AllergenAgent(TemplateAgent):
    """
    Agent for: Allergen information and dietary safety
    
    This agent handles queries related to:
    - Allergen information in dishes
    - Dietary restrictions due to allergies
    - Safe food alternatives for allergies
    - Cross-contamination risks
    
    Example queries this agent should answer:
    - "What allergens are in this dish?"
    - "I'm allergic to dairy, what can I eat?"
    - "Does this contain nuts?"
    """

    def __init__(self):
        """Initialize the agent."""
        super().__init__()
        self.agent_name = "allergen_agent"

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
            # YOUR CUSTOM LOGIC HERE
            # Examples:
            # 1. Simple LLM call (easiest)
            # 2. Database query + LLM
            # 3. External API call + LLM
            # 4. Vector search (RAG) + LLM
            
            # Example: Simple LLM call
            response = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a [your agent type] assistant for a food & beverage system.

Your expertise: [What you specialize in]

User Query: {query}

Provide a helpful, accurate response that:
1. Directly answers the question
2. Includes relevant details and examples
3. Is professional but friendly
4. Is specific to food & beverage context"""
                    }
                ]
            )

            output = response.choices[0].message.content.strip()
            
            return SubAgentResult(
                agent_name=self.agent_name,
                output=output,
                success=True,
                citations=[],  # Add citations if you retrieve from sources
                retrieval_score=0.95,  # Confidence score 0-1
                error=""
            )

        except Exception as e:
            logger.error(f"Agent {self.agent_name} failed: {e}")
            return SubAgentResult(
                agent_name=self.agent_name,
                output="",
                success=False,
                error=str(e)
            )