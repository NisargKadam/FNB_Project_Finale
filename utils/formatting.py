import time
from graph.state import FnBState, EvaluationScore


def print_header():
    print("\n" + "=" * 65)
    print("   F&B Multi-Agent AI System  |  Powered by Claude + LangGraph")
    print("=" * 65 + "\n")


def print_pipeline_step(step: str, detail: str = ""):
    detail_str = f" — {detail}" if detail else ""
    print(f"  [{step}]{detail_str}")


def print_blocked(reason: str):
    print(f"\n  BLOCKED: {reason}\n")


def print_final_response(state: FnBState):
    print("\n" + "-" * 65)
    print(state.final_response)

    if state.citations:
        print("\n  Sources:")
        for c in state.citations:
            print(f"    • {c}")

    score = state.answer_evaluation.overall
    bar = _score_bar(score)
    print(f"\n  Answer Quality: {bar} {score:.0%}")
    print(f"  Time: {state.time_taken_seconds:.2f}s")
    print("-" * 65 + "\n")


def format_eval_score(score: EvaluationScore) -> str:
    return (
        f"Relevance={score.relevance:.0%}  "
        f"Completeness={score.completeness:.0%}  "
        f"Accuracy={score.accuracy:.0%}  "
        f"Overall={score.overall:.0%}"
    )


def _score_bar(score: float, width: int = 10) -> str:
    filled = round(score * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"
