# Agent Development Assignment - Food & Beverage AI System

**Project:** Food & Beverage AI System with Multi-Agent Orchestration  
**Submission Deadline:** [Set by instructor]  
**Workspace:** `c:\Users\nisar\Documents\AI Builder 3\Projects\Final_Project`

---

## 📋 STUDENT ASSIGNMENTS - Each Gets One Agent

| # | Student Name | Assigned Agent | Description |
|---|---|---|---|
| 1 | Sethumeenakshi | recipe_agent | Find and recommend recipes |
| 2 | Abbiramy V Ra | nutrition_agent | Provide nutritional information |
| 3 | Thiagaraj Karthikeyan | menu_agent | Menu items and offerings |
| 4 | tushar bambal | recommendation_agent | Personalized menu recommendations |
| 5 | sindhura Veerabomma | dietary_agent | Handle dietary restrictions |
| 6 | Kavi Suruthi | allergen_agent | Allergen information and safety |
| 7 | Rasika Sudhir Rasal | pricing_agent | Price and cost information |
| 8 | sharandeep singh | inventory_agent | Availability and inventory status |
| 9 | Varshitha Vuyyuru | preparation_time_agent | Cooking/preparation time estimates |
| 10 | Renuka Agarwal | substitution_agent | Ingredient substitutions |
| 11 | Girija Selvakumar | cuisine_agent | Cuisine type and origin info |
| 12 | Sushant Kamble | seasonal_agent | Seasonal and local ingredients |
| 13 | Hareharan KM | beverage_pairing_agent | Wine and drink pairings |
| 14 | Uday Bhanu Bethi | nutrition_calculator_agent | Calorie and macro calculations |
| 15 | Jaya Raju Ganta | restaurant_info_agent | Restaurant details and info |
| 16 | Sripad Mhaddalkar | order_history_agent | Customer order history |
| 17 | Jogula Satya Aditya | trending_agent | Trending dishes and cuisines |
| 18 | Jayesh Hariba Thorat | comparison_agent | Compare multiple items |
| 19 | Khalid Khan | sustainability_agent | Eco-friendly and sustainable options |

**Note:** The full pipeline (guardrails, orchestrator, graph, Streamlit UI) is already built.
You only need to implement your agent file and register it in `subagents/router.py`.

---

## 🖥️ Try the Live UI First

Run the Streamlit UI to see the complete pipeline in action before you start coding:

```bash
streamlit run app.py
```

The UI shows:
- Pipeline stages with status indicators
- Which agents were invoked
- Answer with citations
- Quality scores and timing
- Full pipeline trace (expandable)

Your agent will appear in the **Agents Used** badge once implemented and registered.

---

## 📋 Per-Student Task Details

| Student | Agent | Data Source | Key Test Queries |
|---------|-------|-------------|-----------------|
| Sethumeenakshi | recipe_agent | `data/recipes.json` | "How do I make Biryani?" |
| Abbiramy V Ra | nutrition_agent | `data/nutritional_info.json` | "Calories in Paneer Tikka?" |
| Thiagaraj Karthikeyan | menu_agent | `data/menu_items.json` | "What dishes are available?" |
| Tushar Bambal | recommendation_agent | `data/menu_items.json` | "Suggest a romantic dinner dish" |
| Sindhura Veerabomma | dietary_agent | `data/menu_items.json` | "What vegan options do you have?" |
| Kavi Suruthi | allergen_agent | `data/menu_items.json` + `nutritional_info.json` | "I'm allergic to dairy. What can I eat?" |
| Rasika Sudhir Rasal | pricing_agent | `data/menu_items.json` | "What can I get for under $15?" |
| Sharandeep Singh | inventory_agent | `data/menu_items.json` | "Is Pad Thai available today?" |
| Varshitha Vuyyuru | preparation_time_agent | `data/recipes.json` | "Which dish is quickest to make?" |
| Renuka Agarwal | substitution_agent | `data/recipes.json` | "Can I substitute cream in Paneer Tikka?" |
| Girija Selvakumar | cuisine_agent | `data/menu_items.json` | "What Indian dishes do you have?" |
| Sushant Kamble | seasonal_agent | `data/menu_items.json` | "What's seasonal right now?" |
| Hareharan KM | beverage_pairing_agent | `data/menu_items.json` | "What wine pairs with Beef Tenderloin?" |
| Uday Bhanu Bethi | nutrition_calculator_agent | `data/nutritional_info.json` | "Total calories for Dal Makhani + Mango Lassi?" |
| Jaya Raju Ganta | restaurant_info_agent | Custom data (create `data/restaurant.json`) | "What are your opening hours?" |
| Sripad Mhaddalkar | order_history_agent | Custom data (create `data/orders.json`) | "What's the status of order #1003?" |
| Jogula Satya Aditya | trending_agent | `data/menu_items.json` + popularity scores | "What are your most popular dishes?" |
| Jayesh Hariba Thorat | comparison_agent | `data/menu_items.json` + `nutritional_info.json` | "Compare Caesar Salad and Buddha Bowl" |
| Khalid Khan | sustainability_agent | `data/menu_items.json` | "What's your most eco-friendly dish?" |

---

## 🚀 HOW TO START - Step by Step

### STEP 1: Clone the Project from GitHub

```bash
# Open PowerShell and navigate to where you want the project
cd C:\Users\[YourUsername]\Documents

# Clone the repository (replace with actual Git URL)
git clone https://github.com/[username]/Final_Project.git
cd Final_Project

# Create a new branch for your work (use your agent name)
git checkout -b feature/your_agent_name
# Example:
# git checkout -b feature/recipe_agent
```

### STEP 2: Set Up Your Development Environment

```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
copy .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...
```

### STEP 3: Understand the Project Structure

```
Final_Project/
├── subagents/
│   ├── router.py              ← Master router (DO NOT MODIFY)
│   ├── agent_template.py      ← Template for your agent
│   └── agents/                ← Create your agent here!
│       └── your_agent_name.py
├── main.py                    ← Test your agent here
├── WORKFLOW_GUIDE.md          ← How agents work
└── requirements.txt
```

---

## 💻 BUILDING YOUR AGENT - Step by Step

### Step 3A: Create Your Agent File

**Location:** `subagents/agents/[your_agent_name].py`

**Minimum Implementation (Copy this template):**

```python
"""Your Agent Name - [Brief Description]"""
from subagents.agent_template import TemplateAgent
from graph.state import SubAgentResult
from utils.llm_client import get_client
import logging

logger = logging.getLogger(__name__)


class YourAgentName(TemplateAgent):
    """
    Agent for: [Your assignment description]
    
    This agent handles queries related to:
    - [Main responsibility 1]
    - [Main responsibility 2]
    - [Main responsibility 3]
    
    Example queries this agent should answer:
    - "What is...?"
    - "How do I...?"
    """

    def __init__(self):
        """Initialize the agent."""
        super().__init__()
        self.agent_name = "your_agent_name"

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
                model="gpt-4o-mini",
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
```

### Step 3B: Advanced Options (Optional)

**Option A: Database Query Agent**

```python
def execute(self, query: str, context: dict = None) -> SubAgentResult:
    # 1. Query your data source
    data = self._query_database(query)
    
    # 2. Format for LLM
    context_text = self._format_data(data)
    
    # 3. Generate response with context
    response = self.client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1000,
        messages=[{"role": "user", "content": f"{context_text}\n\nQuestion: {query}"}]
    )
    
    return SubAgentResult(
        agent_name=self.agent_name,
        output=response.choices[0].message.content.strip(),
        success=True
    )

def _query_database(self, query: str) -> list:
    # YOUR DATABASE LOGIC HERE
    return []

def _format_data(self, data: list) -> str:
    # FORMAT DATA FOR LLM
    return "\n".join(str(d) for d in data)
```

**Option B: External API Agent**

```python
def execute(self, query: str, context: dict = None) -> SubAgentResult:
    # 1. Call external API
    import requests
    api_response = requests.get("https://api.example.com/search", params={"q": query})
    
    # 2. Process results
    processed = api_response.json()
    
    # 3. Generate response
    response = self.client.messages.create(...)
    
    return SubAgentResult(...)
```

**Option C: Data File Agent (Using JSON)**

```python
import json

def execute(self, query: str, context: dict = None) -> SubAgentResult:
    # 1. Load data from your data files
    with open("data/menu_items.json") as f:
        data = json.load(f)
    
    # 2. Filter/search data
    results = [item for item in data if "keyword" in item.get("description", "")]
    
    # 3. Generate response
    response = self.client.messages.create(...)
    
    return SubAgentResult(...)
```

---

### Step 3C: Register Your Agent in the Router

**File to Edit:** `subagents/router.py`

Find this section (around line 40):

```python
AVAILABLE_AGENTS = {
    "recipe_agent": "Search and recommend recipes",
    "nutrition_agent": "Provide nutritional information",
    # ... other agents ...
    # ADD YOUR AGENT HERE:
    "your_agent_name": "Your agent description",
}
```

**Then add your agent handler (around line 120):**

```python
def _execute_agent(self, state: FnBState, agent_name: str) -> Optional[SubAgentResult]:
    # ... existing code ...
    
    if agent_name == "your_agent_name":
        from subagents.agents.your_agent_name import YourAgentName
        agent = YourAgentName()
        return agent.execute(state.reformed_query)
    
    # ... rest of code ...
```

---

## 🧪 TESTING YOUR AGENT

### Test 1: Unit Test (Quick Local Test)

**Create file:** `subagents/agents/test_your_agent.py`

```python
"""Test your agent"""
from subagents.agents.your_agent_name import YourAgentName

def test_agent():
    agent = YourAgentName()
    
    # Test case 1: Basic query
    result = agent.execute("What is [your topic]?")
    assert result.success, f"Agent failed: {result.error}"
    assert len(result.output) > 10, "Output too short"
    print("✅ Test 1 passed")
    
    # Test case 2: Another query
    result = agent.execute("How do I [your topic]?")
    assert result.success
    assert "your_agent_name" in result.agent_name
    print("✅ Test 2 passed")
    
    # Test case 3: Error handling
    result = agent.execute("")  # Empty query
    # Should either work or fail gracefully
    print("✅ Test 3 passed")

if __name__ == "__main__":
    test_agent()
    print("\n✅ All tests passed!")
```

**Run your test:**

```bash
python subagents/agents/test_your_agent.py
```

### Test 2: Integration Test (Full Workflow)

**Edit:** `main.py` and add your test query:

```python
# Add to test_queries list:
test_queries = [
    "...",
    "Your test query for your agent?",  # ADD THIS
]
```

**Run full workflow:**

```bash
python main.py
# Your agent should be invoked automatically
```

### Test 3: Direct API Test

```python
# Create test_manual.py:
from graph.main_graph import execute_query

# Test your agent with a query
response = execute_query("Your test query here?")

print("Response:", response)
print("Status:", response.get("status"))
print("Agents Used:", response.get("agents_used"))
print("Answer:", response.get("answer"))
```

**Run it:**

```bash
python test_manual.py
```

---

## 📤 SUBMITTING YOUR WORK - Git Workflow

### Step 1: Commit Your Changes

```bash
# Show what you changed
git status

# Add all your new files
git add subagents/agents/your_agent_name.py
git add subagents/agents/test_your_agent.py

# Commit with clear message
git commit -m "feat: implement your_agent_name agent

- Adds YourAgentName class
- Implements [specific functionality]
- Includes unit tests
- Updates router.py with agent registration"

# Example:
# git commit -m "feat: implement recipe_agent

# - Adds RecipeAgent class for recipe search
# - Uses Claude Sonnet for generation
# - Includes test cases for recipe queries
# - Updates SubAgentRouter with registration"
```

### Step 2: Push Your Branch to GitHub

```bash
# Push your branch
git push origin feature/your_agent_name

# You should see output like:
# remote: Create a pull request for 'feature/your_agent_name' on GitHub by visiting:
# remote: https://github.com/[username]/Final_Project/pull/new/feature/your_agent_name
```

### Step 3: Create a Pull Request (Merge Request)

**Option A: Via GitHub Web Interface (Easy)**

1. Go to: https://github.com/[username]/Final_Project
2. You'll see a banner: "Compare & pull request"
3. Click that button
4. Fill in:
   - **Title:** `feat: Add [Your Agent Name] agent`
   - **Description:** (Use template below)
5. Click "Create Pull Request"

**Option B: Via GitHub CLI**

```bash
gh pr create --title "feat: Add [Your Agent Name] agent" \
             --body "Implements [agent name] for [functionality]"
```

---

### Pull Request Description Template

**Copy this into your PR description:**

```markdown
## Description
Implements the **[Your Agent Name]** agent for the Food & Beverage AI System.

## What does this agent do?
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

## Implementation Details
- Uses [approach: LLM only / Database / API / etc]
- Handles queries like:
  - "What is...?"
  - "How do I...?"
  - "Can you recommend...?"

## Testing
Tested with:
```bash
python subagents/agents/test_your_agent.py
python main.py
```

All tests pass ✅

## Files Changed
- `subagents/agents/your_agent_name.py` - New agent implementation
- `subagents/agents/test_your_agent.py` - Unit tests
- `subagents/router.py` - Agent registration

## Example Query & Response
**Query:** "What is...?"
**Response:** "[Your agent's response]"

## Checklist
- [x] Code follows project conventions
- [x] Unit tests written and passing
- [x] Agent registered in router.py
- [x] Documentation updated
- [x] No breaking changes
```

---

## 📋 COMPLETE CHECKLIST BEFORE SUBMITTING

**Code Quality:**
- [ ] Your agent file: `subagents/agents/your_agent_name.py` ✅
- [ ] Test file: `subagents/agents/test_your_agent.py` ✅
- [ ] Code has comments explaining logic
- [ ] No syntax errors (`python -m py_compile subagents/agents/your_agent_name.py`)
- [ ] Follows naming conventions (snake_case)

**Functionality:**
- [ ] Agent is registered in `subagents/router.py` ✅
- [ ] Agent returns `SubAgentResult` with success flag
- [ ] Agent handles errors gracefully
- [ ] Agent works with empty/invalid input

**Testing:**
- [ ] Unit tests pass locally
- [ ] Integration test works with main.py
- [ ] Manual API test works
- [ ] No breaking changes to other agents

**Documentation:**
- [ ] Code has docstrings
- [ ] Comments explain complex logic
- [ ] PR description is clear and detailed
- [ ] README updated if needed

**Git:**
- [ ] Committed with clear message
- [ ] Pushed to GitHub
- [ ] Pull request opened with description
- [ ] Branch name is: `feature/your_agent_name`

---

## 🆘 TROUBLESHOOTING

### "Module not found" Error
```bash
# Make sure in project directory
cd Final_Project

# Virtual environment activated
venv\Scripts\activate

# All dependencies installed
pip install -r requirements.txt
```

### "OpenAI API key not found"
```bash
# Create .env file with your key
echo OPENAI_API_KEY=sk-... > .env
```

### "Agent not being invoked"
1. Check `AVAILABLE_AGENTS` in `subagents/router.py` - is your agent listed?
2. Check the `if agent_name == "your_agent_name"` in `_execute_agent()` method
3. Restart Python interpreter and try again

### Test shows "success: false"
1. Check the `error` field in result - what's the error message?
2. Run with DEBUG logging: `logging.basicConfig(level=logging.DEBUG)`
3. Read full traceback and fix the issue

### PR shows conflicts
```bash
# Update your branch with latest main
git fetch origin
git merge origin/main
# Fix any conflicts
git add .
git commit -m "Merge main into feature/your_agent_name"
git push origin feature/your_agent_name
```

---

## 📚 HELPFUL RESOURCES

**In Project:**
- `WORKFLOW_GUIDE.md` - How agents work
- `subagents/agent_template.py` - Base class and patterns
- `main.py` - See how agents are tested

**About Your Task:**
- Agent name: Your_Agent_Type
- Role: [Brief description from assignment table above]
- Output: `SubAgentResult` object with `output`, `success`, `error`
- Input: String query from user

**Git Commands:**
```bash
git status              # See what changed
git add filename        # Stage file for commit
git commit -m "..."     # Commit with message
git push origin branch  # Push to GitHub
```

---

## 🎯 SUCCESS CRITERIA

Your agent will be considered complete when:

✅ **Code Quality**
- Implements assign agent functionality
- Handles errors gracefully
- Has clear comments and docstrings
- Passes unit tests

✅ **Integration**
- Registered in SubAgentRouter
- Works in full workflow
- Doesn't break other agents
- Returns proper SubAgentResult

✅ **Testing**
- Unit tests pass
- Integration tests pass  
- Manual testing works
- PR description includes test results

✅ **Documentation**
- Code is well-commented
- PR description is clear
- Explains what agent does

---

## 📞 SUBMISSION DETAILS

**What to Submit:**
- Open Pull Request to `main` branch
- Title: `feat: Add [Agent Name] agent`
- Include test results

**Deadline:** [Set by instructor]

**Grading Criteria:**
- Code quality (40%)
- Functionality (40%)
- Testing (20%)

---

## 🎓 LEARNING OUTCOMES

By completing this assignment, you will:

1. **Understand agent-based architecture** - How individual specialized agents work together
2. **Learn LLM integration** - Calling Claude API with proper prompting
3. **Master Git workflow** - Branching, committing, pull requests
4. **Practice software engineering** - Testing, error handling, documentation
5. **Build scalable systems** - How to extend system to many agents

---

## 📧 Need Help?

If you're stuck:

1. Check `WORKFLOW_GUIDE.md` in the project
2. Review `subagents/agent_template.py` for examples
3. Look at working agents in `router.py`
4. Check test examples in `main.py`
5. Read error messages carefully - they tell you what's wrong

---

## 🚀 Get Started Now!

```bash
# 1. Clone project
git clone <repo_url>
cd Final_Project

# 2. Create branch
git checkout -b feature/your_agent_name

# 3. Create agent file
# subagents/agents/your_agent_name.py

# 4. Test locally
python subagents/agents/test_your_agent_name.py

# 5. Commit and push
git add .
git commit -m "feat: Add your_agent_name"
git push origin feature/your_agent_name

# 6. Open PR on GitHub
# https://github.com/[username]/Final_Project/pulls
```

**Good luck! You've got this! 🚀**

---

## 🚂 Deploying to Railway (Instructor Only)

The project is configured to deploy automatically via `railway.toml`.

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Link to your Railway project
railway link

# 4. Add your OpenAI key as an environment variable in Railway dashboard:
#    Settings → Variables → Add: OPENAI_API_KEY = sk-...

# 5. Deploy
railway up
```

The app will be available at your Railway-generated URL.
Students can use the live URL to test their agents without running locally.
