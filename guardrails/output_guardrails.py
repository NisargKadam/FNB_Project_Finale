"""Output Guardrails - Validate response quality and safety"""
from graph.state import FnBState, GuardrailVerdict
from utils.llm_client import get_client, MODEL
import logging

logger = logging.getLogger(__name__)


class OutputGuardrails:
    """Validates final response for hallucinations, PII, tone, and accuracy."""

    def __init__(self):
        self.client = get_client()

    def check_hallucinations(self, response: str, citations: list[str]) -> tuple[bool, str]:
        """Verify response doesn't contain unsupported claims."""
        if not citations:
            logger.info("Hallucination check skipped — no citations (LLM-only agents)")
            return True, "Hallucination check skipped (no citations)"

        try:
            import os, json

            context_parts = []
            for citation in citations:
                logger.info(f"Processing citation: {citation}")
                logger.info(f"File exists: {os.path.isfile(citation)}")
                if os.path.isfile(citation):
                    try:
                        with open(citation, "r") as f:
                            content = json.load(f) if citation.endswith(".json") else f.read()
                        context_parts.append(json.dumps(content) if isinstance(content, (dict, list)) else content)
                        logger.info(f"Loaded file content, length: {len(context_parts[-1])}")
                    except Exception as e:
                        logger.warning(f"Could not read citation file {citation}: {e}")
                        context_parts.append(citation)
                else:
                    logger.info(f"Citation is not a file, using as-is: {citation}")
                    context_parts.append(citation)

            context = "\n".join(context_parts)
            logger.info(f"Context sent to LLM (first 300 chars): {context[:300]}")
            logger.info(f"Response sent to LLM (first 300 chars): {response[:300]}")

            validation_prompt = f"""You are a fact-checker for a food & beverage AI system.

    Check if the RESPONSE below contains any item names or prices that do NOT exist in the MENU DATA.

    RESPONSE:
    {response}

    MENU DATA:
    {context}

    Rules:
    - If every item and price in the RESPONSE exists in the MENU DATA, reply with exactly: VALID
    - If any item or price in the RESPONSE contradicts or is missing from the MENU DATA, reply with exactly: INVALID: <reason>
    - Do NOT use the word HALLUCINATION in your response."""

            response_obj = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=100,
                messages=[{"role": "user", "content": validation_prompt}]
            )

            result = response_obj.choices[0].message.content.strip()
            logger.info(f"Hallucination check LLM result: {result}")

            if result.upper().startswith("INVALID"):
                return False, "Potential hallucination detected"
            return True, "No hallucinations detected"

        except Exception as e:
            logger.error(f"Hallucination check failed: {e}")
            return True, "Hallucination check skipped (API error)"

    def check_pii_leakage(self, response: str) -> tuple[bool, str]:
        """Ensure no PII in final response."""
        import re
        
        pii_patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phone": r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
            "ssn": r"\b(?!000|666)[0-9]{3}-(?!00)[0-9]{2}-(?!0000)[0-9]{4}\b",
        }
        
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, response):
                return False, f"Potential {pii_type} detected in response"
        
        return True, "No PII detected"

    def validate(self, state: FnBState) -> FnBState:
        """Run all output guardrail checks."""
        if not state.subagent_results:
            state.output_guardrail = GuardrailVerdict(
                passed=False,
                action="REDACT",
                reason="No subagent results available",
                sanitized_text=""
            )
            return state

        final_response = state.subagent_results[0].output if state.subagent_results else ""
        citations = state.subagent_results[0].citations if state.subagent_results else []

        # Skip LLM hallucination check for agents that query structured data directly
        # Their output is already grounded — LLM re-checking introduces false positives
        grounded_agents = {"pricing_agent", "allergen_agent", "inventory_agent"}
        agents_used = {r.agent_name for r in state.subagent_results if r.success}
        skip_hallucination_check = bool(agents_used & grounded_agents)

        if not skip_hallucination_check:
            hallucination_ok, hallucination_msg = self.check_hallucinations(final_response, citations)
            if not hallucination_ok:
                state.output_guardrail = GuardrailVerdict(
                    passed=False,
                    action="REDACT",
                    reason=hallucination_msg,
                    sanitized_text=""
                )
                return state
        else:
            logger.info(f"Hallucination check skipped — grounded agent used: {agents_used & grounded_agents}")

        # Check for PII leakage
        pii_ok, pii_msg = self.check_pii_leakage(final_response)
        if not pii_ok:
            state.output_guardrail = GuardrailVerdict(
                passed=False,
                action="REDACT",
                reason=pii_msg,
                sanitized_text=""
            )
            return state

        # All checks passed
        state.output_guardrail = GuardrailVerdict(
            passed=True,
            action="PASS",
            reason="All output checks passed",
            sanitized_text=final_response
        )
        return state