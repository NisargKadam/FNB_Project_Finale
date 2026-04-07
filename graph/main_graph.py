"""Main Graph - Orchestrates the complete workflow"""
from langgraph.graph import StateGraph, END
from graph.state import FnBState
from guardrails.input_guardrails import InputGuardrails
from guardrails.output_guardrails import OutputGuardrails
from nodes.workflow_nodes import (
    QueryReformationNode,
    OrchestratorNode,
    ResponseAggregationNode,
    AnswerEvaluationNode,
    ToneOfVoiceNode
)
from subagents.router import SubAgentRouter
import logging
import time

logger = logging.getLogger(__name__)


class FnBWorkflow:
    """
    Main workflow orchestrator for Food & Beverage AI system.
    
    Flow:
    1. Query Reformation - Rewrite for clarity
    2. Input Guardrail - Validate input (regex + topic)
    3. Orchestrator - Classify intent and route
    4. Pre-Tool Guardrail - Validate before tool calls
    5. SubAgent Router - Execute 1 or more subagents
    6. Response Aggregation - Merge results
    7. Answer Evaluation - Score response
    8. Output Guardrail - Validate output
    9. Tone of Voice - Align to brand voice
    10. Return Final Response
    """

    def __init__(self):
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()
        self.query_reformer = QueryReformationNode()
        self.orchestrator = OrchestratorNode()
        self.router = SubAgentRouter()
        self.aggregator = ResponseAggregationNode()
        self.evaluator = AnswerEvaluationNode()
        self.tone_checker = ToneOfVoiceNode()
        
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        workflow = StateGraph(FnBState)

        # Add nodes
        workflow.add_node("reform_query", self._node_reform_query)
        workflow.add_node("check_input_guardrail", self._node_input_guardrail)
        workflow.add_node("orchestrate", self._node_orchestrate)
        workflow.add_node("check_pre_tool_guardrail", self._node_pre_tool_guardrail)
        workflow.add_node("execute_agents", self._node_execute_agents)
        workflow.add_node("aggregate_response", self._node_aggregate_response)
        workflow.add_node("evaluate_answer", self._node_evaluate_answer)
        workflow.add_node("check_output_guardrail", self._node_output_guardrail)
        workflow.add_node("tone_of_voice", self._node_tone_of_voice)

        # Build edges
        workflow.add_edge("reform_query", "check_input_guardrail")
        
        # Input guardrail can block or pass
        workflow.add_conditional_edges(
            "check_input_guardrail",
            self._should_continue_after_input_guardrail,
            {
                "continue": "orchestrate",
                "block": END
            }
        )

        workflow.add_edge("orchestrate", "check_pre_tool_guardrail")

        # Pre-tool guardrail validation
        workflow.add_conditional_edges(
            "check_pre_tool_guardrail",
            self._should_continue_after_pre_guardrail,
            {
                "continue": "execute_agents",
                "block": END
            }
        )

        workflow.add_edge("execute_agents", "aggregate_response")
        workflow.add_edge("aggregate_response", "evaluate_answer")
        workflow.add_edge("evaluate_answer", "check_output_guardrail")

        # Output guardrail can redact or pass
        workflow.add_conditional_edges(
            "check_output_guardrail",
            self._should_continue_to_tone,
            {
                "continue": "tone_of_voice",
                "redact": END
            }
        )

        workflow.add_edge("tone_of_voice", END)

        # Set entry point
        workflow.set_entry_point("reform_query")

        return workflow.compile()

    def _node_reform_query(self, state: FnBState) -> FnBState:
        """Node: Reform the query."""
        logger.info(f"=== REFORM QUERY ===\nInput: {state.raw_query}")
        return self.query_reformer.process(state)

    def _node_input_guardrail(self, state: FnBState) -> FnBState:
        """Node: Apply input guardrails."""
        logger.info("=== INPUT GUARDRAIL ===")
        state = self.input_guardrails.validate(state)
        logger.info(f"Status: {state.input_guardrail.action} | {state.input_guardrail.reason}")
        return state

    def _node_orchestrate(self, state: FnBState) -> FnBState:
        """Node: Orchestrate and classify intent."""
        logger.info("=== ORCHESTRATOR ===")
        state = self.orchestrator.process(state)
        logger.info(f"Intent: {state.intent}")
        logger.info(f"Agents: {state.agents_to_invoke}")
        return state

    def _node_pre_tool_guardrail(self, state: FnBState) -> FnBState:
        """Node: Validate parameters before tool execution."""
        logger.info("=== PRE-TOOL GUARDRAIL ===")
        # Validate that we have agents to execute
        if not state.agents_to_invoke:
            state.pre_tool_guardrail = state.input_guardrail  # Reuse verdict
        else:
            state.pre_tool_guardrail.passed = True
            state.pre_tool_guardrail.action = "PASS"
            state.pre_tool_guardrail.reason = "Ready to execute subagents"
        
        logger.info(f"Status: {state.pre_tool_guardrail.action}")
        return state

    def _node_execute_agents(self, state: FnBState) -> FnBState:
        """Node: Execute subagents."""
        logger.info("=== EXECUTE SUBAGENTS ===")
        logger.info(f"Mode: {state.execution_mode}")
        state = self.router.process(state)
        logger.info(f"Results: {len(state.subagent_results)} agents completed")
        return state

    def _node_aggregate_response(self, state: FnBState) -> FnBState:
        """Node: Aggregate responses."""
        logger.info("=== RESPONSE AGGREGATION ===")
        state = self.aggregator.process(state)
        if state.subagent_results:
            logger.info(f"Aggregated output length: {len(state.subagent_results[0].output)}")
        return state

    def _node_evaluate_answer(self, state: FnBState) -> FnBState:
        """Node: Evaluate answer quality."""
        logger.info("=== ANSWER EVALUATION ===")
        state = self.evaluator.process(state)
        if state.subagent_results:
            logger.info(f"Retrieval score: {state.subagent_results[0].retrieval_score:.2f}")
        return state

    def _node_output_guardrail(self, state: FnBState) -> FnBState:
        """Node: Apply output guardrails."""
        logger.info("=== OUTPUT GUARDRAIL ===")
        state = self.output_guardrails.validate(state)
        logger.info(f"Status: {state.output_guardrail.action} | {state.output_guardrail.reason}")
        return state

    def _node_tone_of_voice(self, state: FnBState) -> FnBState:
        """Node: Align to brand voice."""
        logger.info("=== TONE OF VOICE CHECK ===")
        state = self.tone_checker.process(state)
        logger.info("Tone aligned to brand voice")
        return state

    def _should_continue_after_input_guardrail(self, state: FnBState) -> str:
        """Decide if we should continue after input guardrail."""
        return "continue" if state.input_guardrail.passed else "block"

    def _should_continue_after_pre_guardrail(self, state: FnBState) -> str:
        """Decide if we should continue after pre-tool guardrail."""
        return "continue" if state.pre_tool_guardrail.passed else "block"

    def _should_continue_to_tone(self, state: FnBState) -> str:
        """Decide if we should continue to tone check."""
        return "continue" if state.output_guardrail.passed else "redact"

    def run(self, query: str) -> dict:
        """Execute the workflow for a query."""
        logger.info(f"\n{'='*60}")
        logger.info("NEW QUERY RECEIVED")
        logger.info(f"{'='*60}")
        
        start_time = time.time()
        
        # Initialize state
        initial_state = FnBState(raw_query=query)
        
        # Run graph
        result_state = self.graph.invoke(initial_state)
        
        elapsed_time = time.time() - start_time
        
        # Format response
        response = {
            "success": True,
            "query": query,
            "reformed_query": result_state.get("reformed_query", query) if isinstance(result_state, dict) else getattr(result_state, "reformed_query", query),
            "intent": result_state.get("intent", "unknown") if isinstance(result_state, dict) else getattr(result_state, "intent", "unknown"),
            "execution_time_seconds": round(elapsed_time, 2)
        }

        # Check if blocked
        input_guardrail = result_state.get("input_guardrail") if isinstance(result_state, dict) else getattr(result_state, "input_guardrail", None)
        if input_guardrail:
            passed = input_guardrail.get("passed", True) if isinstance(input_guardrail, dict) else getattr(input_guardrail, "passed", True)
            if not passed:
                reason = input_guardrail.get("reason", "Unknown") if isinstance(input_guardrail, dict) else getattr(input_guardrail, "reason", "Unknown")
                message = result_state.get("blocked_message", "") if isinstance(result_state, dict) else getattr(result_state, "blocked_message", "")
                response.update({
                    "success": False,
                    "status": "BLOCKED",
                    "reason": reason,
                    "message": message
                })
                return response

        # Check if redacted
        output_guardrail = result_state.get("output_guardrail") if isinstance(result_state, dict) else getattr(result_state, "output_guardrail", None)
        if output_guardrail:
            passed = output_guardrail.get("passed", True) if isinstance(output_guardrail, dict) else getattr(output_guardrail, "passed", True)
            if not passed:
                reason = output_guardrail.get("reason", "Unknown") if isinstance(output_guardrail, dict) else getattr(output_guardrail, "reason", "Unknown")
                response.update({
                    "success": False,
                    "status": "REDACTED",
                    "reason": reason
                })
                return response

        # Success response
        subagent_results = result_state.get("subagent_results", []) if isinstance(result_state, dict) else getattr(result_state, "subagent_results", [])
        if subagent_results:
            first_result = subagent_results[0]
            output = first_result.get("output", "") if isinstance(first_result, dict) else first_result.output
            citations = first_result.get("citations", []) if isinstance(first_result, dict) else first_result.citations
            
            # Deduplicate agents while preserving order
            agents_used_raw = [
                (r.get("agent_name", "") if isinstance(r, dict) else r.agent_name)
                for r in subagent_results
                if (r.get("success", False) if isinstance(r, dict) else r.success)
            ]
            # Remove duplicates while preserving order
            seen = set()
            agents_used = []
            for agent in agents_used_raw:
                if agent not in seen:
                    agents_used.append(agent)
                    seen.add(agent)
            
            response.update({
                "status": "SUCCESS",
                "answer": output,
                "citations": citations,
                "agents_used": agents_used,
            })
        else:
            response.update({
                "status": "SUCCESS",
                "answer": "I processed your query but no agent returned a result. Please try rephrasing.",
                "citations": [],
                "agents_used": [],
            })

        logger.info(f"\n{'='*60}")
        logger.info("QUERY COMPLETED")
        logger.info(f"Time: {elapsed_time:.2f}s")
        logger.info(f"{'='*60}\n")

        return response


# Lazy-initialized — deferred until first query so Railway env vars
# are guaranteed to be injected before OpenAI clients are created.
_workflow_instance = None


def execute_query(query: str) -> dict:
    """Simple interface to execute a query."""
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = FnBWorkflow()
    return _workflow_instance.run(query)
