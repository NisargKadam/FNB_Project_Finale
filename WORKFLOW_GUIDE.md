"""
WORKFLOW ARCHITECTURE & AGENT DEVELOPMENT GUIDE

This document explains how to extend the system with new subagents beyond the initial 20.

================================================================================
SYSTEM OVERVIEW
================================================================================

The Food & Beverage AI System implements a sophisticated multi-stage workflow:

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. QUERY REFORMATION → 2. INPUT GUARDRAIL → 3. ORCHESTRATOR                │
│                                                        ↓                      │
│ 9. TONE CHECK ← 8. OUTPUT GUARDRAIL ← 7. EVALUATION ← 6. AGGREGATION      │
│     ↓                                                     ↑                  │
│   END                                            5. EXECUTE AGENTS          │
│                                                    ↑                         │
│                                         4. PRE-TOOL GUARDRAIL               │
└─────────────────────────────────────────────────────────────────────────────┘


============================================================
CURRENT AVAILABLE AGENTS (20)
============================================================

1. recipe_agent - Search and recommend recipes
2. nutrition_agent - Provide nutritional information
3. menu_agent - Find menu items and offerings
4. recommendation_agent - Personalized menu recommendations
5. dietary_agent - Handle dietary restrictions
6. allergen_agent - Allergen information and safety
7. pricing_agent - Price and cost queries
8. inventory_agent - Availability and inventory status
9. preparation_time_agent - Cooking/preparation times
10. substitution_agent - Ingredient substitutions
11. cuisine_agent - Cuisine type and origin info
12. seasonal_agent - Seasonal and local ingredients
13. beverage_pairing_agent - Wine and drink pairings
14. nutrition_calculator_agent - Detailed nutrition calculations
15. restaurant_info_agent - Restaurant information
16. order_history_agent - Customer order history
17. trending_agent - Trending and popular items
18. comparison_agent - Compare multiple items
19. sustainability_agent - Sustainability and eco-friendly options
20. feedback_agent - Reviews and customer feedback


============================================================
HOW THE ROUTER WORKS
============================================================

The SubAgentRouter (subagents/router.py) is the master orchestrator that:

1. ORCHESTRATOR sends list of agents to invoke
   - Queries: recipe_agent, nutrition_agent
   - Queries: recommendation_agent

2. ROUTER determines execution mode
   - PARALLEL: Up to 5 agents run simultaneously (ThreadPoolExecutor)
   - SEQUENTIAL: Agents run one at a time

3. ROUTER delegates to individual agents
   - Each agent receives the reformed query
   - Each agent returns SubAgentResult with output + citations

4. RESULTS aggregated and processed downstream
   - Aggregation node merges outputs
   - Evaluation node scores quality
   - Guardrails validate safety


============================================================
ADDING A NEW AGENT - STEP BY STEP
============================================================

Step 1: Register the Agent in the Router
─────────────────────────────────────────
Edit: subagents/router.py

Add entry to AVAILABLE_AGENTS dictionary:

    AVAILABLE_AGENTS = {
        ...
        "your_new_agent": "Description of what it does",
        ...
    }


Step 2: Optional - Create Specialized Agent Class
──────────────────────────────────────────────────
Create: subagents/agents/your_agent.py (optional structure)

    class YourAgent:
        def __init__(self):
            self.client = get_client()
        
        def execute(self, query: str) -> str:
            # Your custom logic here
            response = self.client.messages.create(...)
            return response.content[0].text.strip()


Step 3: Update Router to Use Custom Agent
───────────────────────────────────────────
Option A: Inline (simple agents - already supported)
   The router automatically sends queries to agents based on their
   description. For simple LLM-based agents, no code change needed!

Option B: Custom Handler (complex agents)
   Modify the _execute_agent method in router.py to handle specialized logic:

    def _execute_agent(self, state: FnBState, agent_name: str):
        ...
        if agent_name == "your_new_agent":
            # Import and use your custom agent
            from subagents.agents.your_agent import YourAgent
            agent = YourAgent()
            output = agent.execute(state.reformed_query)
        ...


Step 4: Test Your Agent
───────────────────────
    from graph.main_graph import execute_query
    
    response = execute_query("Your test query")
    print(response)


============================================================
AGENT EXECUTION PATTERNS
============================================================

SIMPLE LLM-BASED AGENT (Requires: Function Definition Only)
────────────────────────────────────────────────────────────
// Just register in AVAILABLE_AGENTS - router handles it!

AGENT WITH RAG (Vector Search)
───────────────────────────────
    def _execute_agent(self, ...):
        # 1. Retrieve relevant documents from ChromaDB
        search_results = rag_client.search(query, top_k=5)
        
        # 2. Pass context to agent
        context = format_search_results(search_results)
        
        # 3. Generate response with context
        response = client.messages.create(
            messages=[{"role": "user", "content": f"{context}\n\n{query}"}]
        )
        
        # 4. Return results with citations
        return SubAgentResult(
            output=response.content[0].text,
            citations=extract_sources(search_results)
        )


AGENT WITH EXTERNAL API CALL
──────────────────────────────
    def _execute_agent(self, ...):
        # 1. Call external API (database, service, etc)
        external_data = fetch_from_api(query_params)
        
        # 2. Process results
        formatted_data = process_response(external_data)
        
        # 3. Generate response
        response = client.messages.create(
            messages=[...formatted_data...]
        )
        
        return SubAgentResult(output=response)


AGENT WITH STATE MANAGEMENT (For sequential dependencies)
──────────────────────────────────────────────────────────
    def _execute_agent(self, state: FnBState, agent_name: str):
        # Access state.subagent_results to see prior agent outputs
        previous_results = state.subagent_results
        
        # Use previous context in new query
        context = "\n".join([r.output for r in previous_results])
        
        response = client.messages.create(
            messages=[{"role": "user", "content": f"{context}\n\n{state.reformed_query}"}]
        )


============================================================
MODIFYING ORCHESTRATOR ROUTING
============================================================

The Orchestrator (nodes/workflow_nodes.py) decides which agents to invoke
based on intent classification.

Current intent classifications:
  - recipe_search
  - nutrition_info
  - menu_info
  - recommendations
  - dietary_advice
  - other

To add new intents and agent mappings:

Edit: nodes/workflow_nodes.py - OrchestratorNode.process()

Add custom routing:
    if state.intent == "new_intent":
        state.agents_to_invoke = ["agent_1", "agent_2"]
        state.execution_mode = "parallel"


============================================================
GUARDRAIL CUSTOMIZATION
============================================================

INPUT GUARDRAILS (guardrails/input_guardrails.py)
──────────────────────────────────────────────────
Blocks: PII, profanity, SQL injection, off-topic
Add custom checks: 

    def custom_check(self, text: str) -> tuple[bool, Optional[str]]:
        # Your custom logic
        return True, None


OUTPUT GUARDRAILS (guardrails/output_guardrails.py)
────────────────────────────────────────────────────
Validates: No hallucinations, no PII, quality checks
Add custom validation:

    def check_custom_criteria(self, response: str) -> tuple[bool, str]:
        # Your validation logic
        return True, "Passed"


============================================================
RESPONSE EVALUATION SCORING
============================================================

The evaluation node scores responses on:
  - Relevance (0-1): How well does it answer the query?
  - Completeness (0-1): Is information sufficient?
  - Accuracy (0-1): Is information correct?
  - Overall: Average of above

High scores (>0.8) bypass output guardrails.
Low scores (<0.5) trigger re-attempts with RAG reformulation.


============================================================
EXAMPLE: Adding a "menu_filtering_agent"
============================================================

File: subagents/agents/menu_filtering_agent.py
──────────────────────────────────────────────

    from utils.llm_client import get_client
    from graph.state import SubAgentResult
    
    class MenuFilteringAgent:
        def __init__(self):
            self.client = get_client()
        
        def filter_menu(self, query: str, filters: dict) -> SubAgentResult:
            # Apply dietary filters, price range, cuisine type, etc.
            filter_string = self._format_filters(filters)
            
            response = self.client.chat.completions.create(
                model="gpt-4-mini",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"""Filter menu items based on these criteria:
{filter_string}

User Query: {query}

Return filtered results with descriptions."""
                }]
            )
            
            return SubAgentResult(
                agent_name="menu_filtering_agent",
                output=response.content[0].text.strip(),
                success=True,
                retrieval_score=0.95
            )
        
        def _format_filters(self, filters: dict) -> str:
            lines = []
            for key, value in filters.items():
                lines.append(f"- {key}: {value}")
            return "\n".join(lines)


Router Update: subagents/router.py
──────────────────────────────────

    AVAILABLE_AGENTS = {
        ...
        "menu_filtering_agent": "Filter menu items by dietary/price/cuisine",
    }
    
    def _execute_agent(self, state: FnBState, agent_name: str):
        ...
        if agent_name == "menu_filtering_agent":
            from subagents.agents.menu_filtering_agent import MenuFilteringAgent
            agent = MenuFilteringAgent()
            filters = self._extract_filters(state.reformed_query)
            return agent.filter_menu(state.reformed_query, filters)
        ...


============================================================
PERFORMANCE OPTIMIZATION
============================================================

Parallel Execution:
  - Set execution_mode="parallel" in orchestrator
  - Max 5 agents: ThreadPoolExecutor(max_workers=5)
  - Best for: Independent queries (recipe + nutrition)

Sequential Execution:
  - Set execution_mode="sequential"
  - Each agent uses results from prior agents
  - Best for: Dependent queries (filter → price → nutrition)

Custom Timeout:
    executor.submit(agent_task, timeout=30)
    # Default: 30 seconds per agent
    # Adjust in SubAgentRouter._execute_parallel()


============================================================
DEBUGGING & LOGGING
============================================================

Enable detailed logging:

    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    from graph.main_graph import execute_query
    response = execute_query("Your query")
    
    # Check logs for:
    # - Which agents were invoked
    # - Execution time per node
    # - Guardrail verdicts
    # - Error messages


Test individual agents:

    from subagents.router import SubAgentRouter
    router = SubAgentRouter()
    result = router._execute_agent(state, "recipe_agent")
    print(result)


============================================================
DEPLOYMENT CHECKLIST
============================================================

Before deploying new agents:

[ ] Agent is registered in AVAILABLE_AGENTS
[ ] Agent output is well-formed and consistently structured
[ ] Agent includes appropriate error handling
[ ] Agent respects timeout limits (30 seconds max)
[ ] Citations/sources are properly formatted
[ ] Input validation and sanitization is in place
[ ] Output passes guardrail checks
[ ] Performance meets requirements (latency < 5s total)
[ ] Comprehensive logging is enabled
[ ] Unit tests are written
[ ] Documentation is updated
"""
