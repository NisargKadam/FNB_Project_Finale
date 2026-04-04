# Student Agent Assignments - Quick Reference

## Your Assignment

Find your name below to see which agent you're building:

| Name | Agent | Task |
|------|-------|------|
| **Sethumeenakshi** | 🍳 **recipe_agent** | Find and recommend recipes |
| **Abbiramy V Ra** | 🥗 **nutrition_agent** | Provide nutritional information |
| **Thiagaraj Karthikeyan** | 📋 **menu_agent** | Menu items and offerings |
| **tushar bambal** | 🎯 **recommendation_agent** | Personalized menu recommendations |
| **sindhura Veerabomma** | 🚫 **dietary_agent** | Handle dietary restrictions |
| **Kavi Suruthi** | ⚠️ **allergen_agent** | Allergen information and safety |
| **Rasika Sudhir Rasal** | 💰 **pricing_agent** | Price and cost information |
| **sharandeep singh** | 📦 **inventory_agent** | Availability and inventory status |
| **Varshitha Vuyyuru** | ⏱️ **preparation_time_agent** | Cooking/preparation time estimates |
| **Renuka Agarwal** | 🔄 **substitution_agent** | Ingredient substitutions |
| **Girija Selvakumar** | 🌍 **cuisine_agent** | Cuisine type and origin info |
| **Sushant Kamble** | 🌱 **seasonal_agent** | Seasonal and local ingredients |
| **Hareharan KM** | 🍷 **beverage_pairing_agent** | Wine and drink pairings |
| **Uday Bhanu Bethi** | 📊 **nutrition_calculator_agent** | Calorie and macro calculations |
| **Jaya Raju Ganta** | 🏪 **restaurant_info_agent** | Restaurant details and info |
| **Sripad Mhaddalkar** | 📜 **order_history_agent** | Customer order history |
| **Jogula Satya Aditya** | 🔥 **trending_agent** | Trending dishes and cuisines |
| **Jayesh Hariba Thorat** | ⚖️ **comparison_agent** | Compare multiple items |
| **Khalid Khan** | ♻️ **sustainability_agent** | Eco-friendly and sustainable options |

---

## Quick Start (5 Minutes)

```bash
# 1. Clone the project
git clone <repo_url>
cd Final_Project

# 2. Create your development branch
git checkout -b feature/your_agent_name

# 3. Look at the template
# Open: subagents/agent_template.py

# 4. Create your agent
# File: subagents/agents/your_agent_name.py
# Copy template and customize!

# 5. Register your agent
# Edit: subagents/router.py (2 small changes)

# 6. Test it
python subagents/agents/test_your_agent_name.py
python main.py

# 7. Submit
git add .
git commit -m "feat: Add your_agent_name agent"
git push origin feature/your_agent_name
# Then open Pull Request on GitHub
```

---

## File You Need to Create

**Location:** `subagents/agents/[your_agent_name].py`

**Template:**
```python
from subagents.agent_template import TemplateAgent
from graph.state import SubAgentResult

class YourAgentClass(TemplateAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "your_agent_name"
    
    def execute(self, query: str, context: dict = None) -> SubAgentResult:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-mini",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"You are a [your agent type]. Answer: {query}"
                }]
            )
            return SubAgentResult(
                agent_name=self.agent_name,
                output=response.choices[0].message.content.strip(),
                success=True
            )
        except Exception as e:
            return SubAgentResult(
                agent_name=self.agent_name,
                output="",
                success=False,
                error=str(e)
            )
```

---

## File You Need to Modify

**Location:** `subagents/router.py`

**Change 1 - Around line 40:**
```python
AVAILABLE_AGENTS = {
    "recipe_agent": "Search and recommend recipes",
    # ... other agents ...
    "your_agent_name": "Your description here",  # ADD THIS
}
```

**Change 2 - Around line 120 in _execute_agent method:**
```python
def _execute_agent(self, state: FnBState, agent_name: str):
    # ... existing code ...
    if agent_name == "your_agent_name":
        from subagents.agents.your_agent_name import YourAgentClass
        agent = YourAgentClass()
        return agent.execute(state.reformed_query)
    # ... rest of code ...
```

---

## Important Files to Reference

📚 **STUDENT_ASSIGNMENTS.md** - Full step-by-step guide (READ THIS!)  
📚 **subagents/agent_template.py** - Code templates (copy and modify)  
📚 **WORKFLOW_GUIDE.md** - How agents work (advanced patterns)  

---

## Testing Your Agent

```bash
# Create file: subagents/agents/test_your_agent_name.py
python subagents/agents/test_your_agent_name.py

# Should output:
# ✅ Test 1 passed
# ✅ Test 2 passed
# ✅ All tests passed!
```

---

## Submitting (Git)

```bash
# See your changes
git status

# Add your files
git add subagents/agents/your_agent_name.py
git add subagents/agents/test_your_agent_name.py

# Commit with message
git commit -m "feat: Add your_agent_name agent"

# Push to GitHub
git push origin feature/your_agent_name

# Open Pull Request on GitHub
# https://github.com/username/Final_Project/pulls
```

---

## Success Checklist

- [ ] Agent file created: `subagents/agents/your_agent_name.py`
- [ ] Agent class implements `execute()` method
- [ ] Returns `SubAgentResult` with output and success flag
- [ ] Registered in `subagents/router.py` AVAILABLE_AGENTS
- [ ] Handler added to `_execute_agent()` method in router
- [ ] Test file created and passes
- [ ] Works with `python main.py`
- [ ] Committed with clear message
- [ ] Push to GitHub
- [ ] Pull Request opened

---

## Need Help?

1. **How to start?** Read STUDENT_ASSIGNMENTS.md (has full step-by-step guide)
2. **Code example?** Look at subagents/agent_template.py
3. **How to register?** See router.py comments  
4. **How to test?** Run `python main.py` and check logs
5. **Git issues?** See STUDENT_ASSIGNMENTS.md Git section

---

**Deadline:** Check with your instructor  
**Questions?** Ask in class or office hours

**You're building a real AI agent system! Good luck!** 🚀
