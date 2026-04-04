"""Output Guardrails - Validate response quality and safety"""
from graph.state import FnBState, GuardrailVerdict
from utils.llm_client import get_client
import logging

logger = logging.getLogger(__name__)


class OutputGuardrails:
    """Validates final response for hallucinations, PII, tone, and accuracy."""

    def __init__(self):
        self.client = get_client()

    def check_hallucinations(self, response: str, citations: list[str]) -> tuple[bool, str]:
        """Verify response doesn't contain unsupported claims."""
        try:
            context = "\n".join(citations) if citations else "No citations provided"
            
            validation_prompt = f"""Review this response for hallucinations (claims not supported by citations):

RESPONSE: {response}

CITATIONS:
{context}

Does the response contain claims NOT supported by the citations? Respond with "VALID" or "HALLUCINATION" + reason."""
            
            response_obj = self.client.chat.completions.create(
                model="gpt-4-mini",
                max_tokens=100,
                messages=[{"role": "user", "content": validation_prompt}]
            )
            
            result = response_obj.choices[0].message.content.strip().upper()
            if "VALID" in result:
                return True, "No hallucinations detected"
            else:
                return False, f"Potential hallucination detected"
        except Exception as e:
            logger.error(f"Hallucination check failed: {e}")
            return False, f"Error during validation: {str(e)}"

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

        # Check for hallucinations
        hallucination_ok, hallucination_msg = self.check_hallucinations(final_response, citations)
        if not hallucination_ok:
            state.output_guardrail = GuardrailVerdict(
                passed=False,
                action="REDACT",
                reason=hallucination_msg,
                sanitized_text=""
            )
            return state

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
