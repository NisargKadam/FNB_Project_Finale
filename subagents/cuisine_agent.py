from utils.llm_client import MODEL
from graph.state import SubAgentResult
class CuisineAgent:

    def __init__(self, client):
        self.client = client
        self.model = MODEL

    def execute(self, query: str, context: dict):

        context_text = ""

        # VECTOR (list of strings)
        for item in context.get("vector", []):
            context_text += f"[VECTOR] {item}\n"

        # LOCAL (dict list)
        for item in context.get("local", []):
            context_text += (
                f"[LOCAL] {item.get('name', '')} | "
                f"{item.get('description', '')}\n"
            )

        # WEB (dict)
        web = context.get("web", {})
        if web.get("success"):
            for item in web.get("data", []):
                context_text += (
                    f"[WEB] {item.get('title', '')} | "
                    f"{item.get('body', '')}\n"
                )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": f"""
You are a cuisine expert.

Use this context:

{context_text}

Question:
{query}
"""
            }]
        )

        return SubAgentResult(
    agent_name="cuisine_agent",
    output=response.choices[0].message.content,
    success=True,
    citations=[],
    retrieval_score=1.0,
    error=""
)