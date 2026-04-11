"""Nodes for the main workflow"""
from graph.state import FnBState
from utils.llm_client import get_client, MODEL
import logging

logger = logging.getLogger(__name__)


class QueryReformationNode:
    """Reformats user query for clarity and expands abbreviations."""

    def __init__(self):
        self.client = get_client()

    def process(self, state: FnBState) -> FnBState:
        """Rewrite query for clarity."""
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=200,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Rewrite this query for clarity. Expand abbreviations, fix typos, and make it more specific for food & beverage context:

Original: "{state.raw_query}"

Provide ONLY the reformatted query, no explanation."""
                    }
                ]
            )
            state.reformed_query = response.choices[0].message.content.strip()
            logger.info(f"Original: {state.raw_query}")
            logger.info(f"Reformed: {state.reformed_query}")
        except Exception as e:
            logger.error(f"Query reformation failed: {e}")
            state.reformed_query = state.raw_query

        return state


class OrchestratorNode:
    """Classifies intent and determines which subagents to invoke."""

    def __init__(self):
        self.client = get_client()

    def process(self, state: FnBState) -> FnBState:
        """Classify intent and route to appropriate agents."""
        try:
            response = self.client.chat.completions.create(
    model=MODEL,
    max_tokens=300,
    messages=[
        {
            "role": "user",
            "content": f"""Classify the intent of this query and suggest which agents should handle it.

Query: "{state.reformed_query}"

INTENT options:
- recipe_search: user wants a recipe or cooking instructions
- nutrition_info: user asks about calories, macros, or health info
- menu_info: user wants to know what is on the menu
- recommendations: user wants suggestions (no price constraint)
- dietary_advice: user has dietary restrictions or allergies
- pricing: user asks about cost, price, budget, or what they can get for a certain amount of money
- other: anything else

AGENT options:
recipe_agent, nutrition_agent, menu_agent, recommendation_agent, dietary_agent, allergen_agent, pricing_agent

RULES:
- If the query contains words like "under", "below", "less than", "over", "above", "budget", "$", "afford", or any dollar amount — ALWAYS use pricing_agent and set INTENT to pricing.
- Only pick agents relevant to the query. Usually 1 agent is enough.

Respond in this exact format:
INTENT: [intent]
AGENTS: [comma-separated agent names]
REASONING: [brief explanation]
EXECUTION_MODE: [parallel or sequential]"""
        }
    ]
)
            
            response_text = response.choices[0].message.content.strip()
            # Parse response
            lines = response_text.split("\n")
            for line in lines:
                if line.startswith("INTENT:"):
                    state.intent = line.split(":", 1)[1].strip()
                elif line.startswith("AGENTS:"):
                    agents_str = line.split(":", 1)[1].strip()
                    state.agents_to_invoke = [a.strip() for a in agents_str.split(",")]
                elif line.startswith("EXECUTION_MODE:"):
                    state.execution_mode = line.split(":", 1)[1].strip().lower()

            logger.info(f"Intent: {state.intent}")
            logger.info(f"Agents to invoke: {state.agents_to_invoke}")
            logger.info(f"Execution mode: {state.execution_mode}")
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            state.intent = "other"
            state.agents_to_invoke = ["general_agent"]
            state.execution_mode = "sequential"

        return state


class ResponseAggregationNode:
    """Merges results from multiple subagents into coherent response."""

    def __init__(self):
        self.client = get_client()

    def process(self, state: FnBState) -> FnBState:
        """Aggregate subagent results into final response."""
        if not state.subagent_results:
            return state

        successful_results = [r for r in state.subagent_results if r.success]

        # Skip LLM aggregation for single results OR grounded agents
        grounded_agents = {"pricing_agent", "allergen_agent", "inventory_agent"}
        agents_used = {r.agent_name for r in successful_results}

        if len(successful_results) == 1 or bool(agents_used & grounded_agents):
            logger.info("Skipping LLM aggregation — single or grounded agent result")
            return state

        try:
            aggregated_results = "\n\n".join(
                [f"From {r.agent_name}:\n{r.output}" for r in successful_results]
            )

            all_citations = []
            for r in state.subagent_results:
                all_citations.extend(r.citations)

            response = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Synthesize these results into a cohesive, well-organized response.
    DO NOT add any items, prices, or facts not explicitly present in the source results below.

    {aggregated_results}

    Create a unified answer that:
    1. Avoids redundancy
    2. Presents information logically
    3. Maintains accuracy from source information — do not invent or add any new items
    4. Is written in professional but friendly tone for food & beverage context"""
                    }
                ]
            )

            if state.subagent_results:
                state.subagent_results[0].output = response.choices[0].message.content.strip()
                state.subagent_results[0].citations = all_citations

            logger.info("Response aggregated successfully")
        except Exception as e:
            logger.error(f"Response aggregation failed: {e}")

        return state

class AnswerEvaluationNode:
    """Scores response for relevance, completeness, and accuracy."""

    def __init__(self):
        self.client = get_client()

    def process(self, state: FnBState) -> FnBState:
        """Evaluate response quality."""
        if not state.subagent_results:
            return state

        try:
            response_text = state.subagent_results[0].output
            
            evaluation_prompt = f"""Evaluate this response on a scale of 0-1:

ORIGINAL QUERY: "{state.reformed_query}"
RESPONSE: "{response_text}"

Score on:
1. RELEVANCE: How directly does it answer the query?
2. COMPLETENESS: Does it provide sufficient detail?
3. ACCURACY: Is the information accurate?

Respond in format:
RELEVANCE: [0-1]
COMPLETENESS: [0-1]
ACCURACY: [0-1]
OVERALL: [average of above]
FEEDBACK: [brief assessment]"""

            response = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=200,
                messages=[{"role": "user", "content": evaluation_prompt}]
            )

            response_text = response.choices[0].message.content.strip()
            # Parse scores
            lines = response_text.split("\n")
            scores = {}
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    try:
                        if key in ["RELEVANCE", "COMPLETENESS", "ACCURACY", "OVERALL"]:
                            scores[key.lower()] = float(value.strip())
                        elif key == "FEEDBACK":
                            scores["feedback"] = value.strip()
                    except ValueError:
                        pass

            # Store evaluation in state
            if state.subagent_results:
                state.subagent_results[0].retrieval_score = scores.get("overall", 0.0)
            
            logger.info(f"Evaluation scores: {scores}")
        except Exception as e:
            logger.error(f"Answer evaluation failed: {e}")

        return state


class ToneOfVoiceNode:
    """Ensures response matches brand voice: professional, friendly, F&B focused."""

    def __init__(self):
        self.client = get_client()

    def process(self, state: FnBState) -> FnBState:
        """Check and potentially adjust tone."""
        if not state.subagent_results:
            return state

        try:
            response_text = state.subagent_results[0].output
            
            tone_prompt = f"""Review this response for brand voice alignment. Adjust if needed:

RESPONSE: "{response_text}"

The brand voice for food & beverage should be:
- Professional but friendly
- Knowledgeable but accessible
- Food-centric and enthusiastic about cuisine
- Helpful and welcoming

If adjustment is needed, rewrite the response. Otherwise, keep it as-is but add a brief tone assessment.

Respond with the revised response or original if no changes needed."""

            response = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=1000,
                messages=[{"role": "user", "content": tone_prompt}]
            )

            adjusted_response = response.choices[0].message.content.strip()
            if state.subagent_results:
                state.subagent_results[0].output = adjusted_response
            
            logger.info("Tone aligned to brand voice")
        except Exception as e:
            logger.error(f"Tone adjustment failed: {e}")

        return state
