import operator
from typing import Annotated
from pydantic import BaseModel, Field


class SubAgentResult(BaseModel):
    agent_name: str = ""
    output: str = ""
    citations: list[str] = []
    retrieval_score: float = 0.0
    success: bool = False
    error: str = ""


class GuardrailVerdict(BaseModel):
    passed: bool = True
    action: str = "PASS"       # PASS | BLOCK | REDACT
    reason: str = ""
    sanitized_text: str = ""


class EvaluationScore(BaseModel):
    relevance: float = 0.0
    completeness: float = 0.0
    accuracy: float = 0.0
    overall: float = 0.0
    feedback: str = ""


class FnBState(BaseModel):
    # Input
    raw_query: str = ""
    reformed_query: str = ""
    sanitized_query: str = ""

    # Routing
    intent: str = ""
    agents_to_invoke: list[str] = []
    execution_mode: str = "sequential"

    # Guardrails
    input_guardrail: GuardrailVerdict = Field(default_factory=GuardrailVerdict)
    pre_tool_guardrail: GuardrailVerdict = Field(default_factory=GuardrailVerdict)
    output_guardrail: GuardrailVerdict = Field(default_factory=GuardrailVerdict)
    blocked_message: str = ""

    # SubAgent results — Annotated so parallel nodes can fan-in safely
    subagent_results: Annotated[list[SubAgentResult], operator.add] = []
    retrieval_attempts: int = 0
    max_retrieval_attempts: int = 2

    # Evaluation
    search_evaluation_passed: bool = False
    answer_evaluation: EvaluationScore = Field(default_factory=EvaluationScore)

    # Response
    aggregated_response: str = ""
    tone_checked_response: str = ""
    final_response: str = ""
    citations: list[str] = []

    # Timing
    start_time: float = 0.0
    time_taken_seconds: float = 0.0

    # Audit trail — Annotated for parallel fan-in
    messages: Annotated[list[str], operator.add] = []
