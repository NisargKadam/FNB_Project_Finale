"""Input Guardrails - Regex and Agent-based validation"""
import re
from typing import Optional
from graph.state import FnBState, GuardrailVerdict
from utils.llm_client import get_client, MODEL
import logging

logger = logging.getLogger(__name__)


class InputGuardrails:
    """Validates user input for PII, profanity, SQL injection, and topic relevance."""

    # Regex patterns for common threats
    PII_PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
        "ssn": r"\b(?!000|666)[0-9]{3}-(?!00)[0-9]{2}-(?!0000)[0-9]{4}\b",
        "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    }

    PROFANITY_PATTERNS = {
        "common_profanity": r"\b(badword1|badword2|badword3)\b",  # Replace with actual patterns
    }

    SQL_INJECTION_PATTERNS = {
        "sql_inject": r"('|(--)|;|(\*)|(\bOR\b)|(\bAND\b)|(\bUNION\b))",
    }

    def __init__(self):
        self.client = get_client()

    def regex_check(self, text: str) -> tuple[bool, Optional[str]]:
        """Run regex-based checks for PII, profanity, SQL injection."""
        checks = {**self.PII_PATTERNS, **self.PROFANITY_PATTERNS, **self.SQL_INJECTION_PATTERNS}
        
        for check_name, pattern in checks.items():
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Detected {check_name}"
        
        return True, None

    def topic_relevance_check(self, query: str) -> tuple[bool, str]:
        """Use LLM to verify query is food & beverage related."""
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Is this query related to food, beverages, nutrition, recipes, or restaurant information?
                        
Query: "{query}"

Respond ONLY with "YES" or "NO". If NO, provide brief reason."""
                    }
                ]
            )
            answer = response.choices[0].message.content.strip().upper()
            
            if answer.startswith("YES"):
                return True, "Topic is food & beverage related"
            else:
                return False, "Query not food & beverage related"
        except Exception as e:
            logger.error(f"Topic check failed: {e}")
            return False, f"Error during topic check: {str(e)}"

    def validate(self, state: FnBState) -> FnBState:
        """Run all input guardrail checks."""
        query = state.raw_query
        
        # 1. Regex checks
        regex_passed, regex_reason = self.regex_check(query)
        if not regex_passed:
            state.input_guardrail = GuardrailVerdict(
                passed=False,
                action="BLOCK",
                reason=f"Regex check failed: {regex_reason}",
                sanitized_text=""
            )
            state.blocked_message = f"Query blocked: {regex_reason}"
            return state

        # 2. Topic relevance check
        topic_passed, topic_reason = self.topic_relevance_check(query)
        if not topic_passed:
            state.input_guardrail = GuardrailVerdict(
                passed=False,
                action="BLOCK",
                reason=f"Topic check failed: {topic_reason}",
                sanitized_text=""
            )
            state.blocked_message = f"Query blocked: {topic_reason}"
            return state

        # All checks passed
        state.input_guardrail = GuardrailVerdict(
            passed=True,
            action="PASS",
            reason="All checks passed",
            sanitized_text=query
        )
        return state
