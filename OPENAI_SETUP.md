# OpenAI API Configuration Guide

## Model Information

**Current Model:** `gpt-4-mini` (OpenAI's cost-effective GPT-4 variant)

### Why GPT-4 Mini?
- ✅ **Performance:** Near GPT-4 performance at lower cost
- ✅ **Speed:** Faster response times than full GPT-4
- ✅ **Cost:** Significantly cheaper than Claude Sonnet
- ✅ **Analysis:** Excellent at logical reasoning and multi-step tasks
- ✅ **Reliable:** Production-ready and well-tested

### Model Capabilities
- Max context: 128K tokens
- Output: Up to 4K tokens per request
- Function calling: ✅ Supported
- Vision: ✅ Supported (if needed in future)

---

## Setup Instructions

### 1. Get Your OpenAI API Key

1. Go to https://platform.openai.com/api/keys
2. Sign up or log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (you'll only see it once!)

### 2. Set up .env File

```bash
# Copy the example env file
copy .env.example .env

# Edit .env and add your key
OPENAI_API_KEY=sk-...your-key-here...
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Pricing (as of April 2026)

| Model | Input | Output |
|-------|-------|--------|
| gpt-4-mini | $0.015 / 1K tokens | $0.06 / 1K tokens |
| gpt-4 | $0.03 / 1K tokens | $0.06 / 1K tokens |

**Expected Cost per Query:**
- Average query: ~500 input + 200 output tokens
- Cost per query: ~$0.01-0.02
- 1000 queries: ~$10-20

---

## Testing Your Setup

### Quick Test

```python
from utils.llm_client import get_client
from graph.state import SubAgentResult

client = get_client()
response = client.chat.completions.create(
    model="gpt-4-mini",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Full Integration Test

```bash
python main.py
```

Expected output: 4 test queries successfully processed

---

## Troubleshooting

### "OpenAI APIError: Authentication failed"
- [ ] Check your API key is correctly set in .env
- [ ] Make sure the key starts with `sk-`
- [ ] Regenerate key if it's old

### "RateLimitError"
- [ ] You've exceeded OpenAI's rate limits
- [ ] Wait a few seconds and retry
- [ ] Check your usage at https://platform.openai.com/account/usage

### "Connection error"
- [ ] Check internet connection
- [ ] OpenAI API might be temporarily down
- [ ] Try again in a few moments

### Very slow responses
- [ ] gpt-4-mini should respond in <5 seconds
- [ ] If slower, check internet speed
- [ ] OpenAI servers might be busy

---

## API Response Format

OpenAI uses a different response format than Anthropic:

**OpenAI Response:**
```python
response = client.chat.completions.create(...)
text = response.choices[0].message.content
```

**Key differences:**
- Use `chat.completions.create()` not `messages.create()`
- Access response via `choices[0].message.content`, not `content[0].text`
- Messages format is the same

All of these are already updated in the project code!

---

## Best Practices

1. **Caching:** Consider caching responses for identical queries
2. **Cost Control:** Set max_tokens to avoid runaway costs
3. **Error Handling:** Always catch API exceptions
4. **Monitoring:** Track token usage and costs
5. **Timeouts:** Set reasonable request timeouts

---

## Advanced Configuration

### Using Different Models (Optional)

To use a different OpenAI model, edit `utils/llm_client.py`:

```python
MODEL = "gpt-4"  # Use full GPT-4 (more expensive)
# or
MODEL = "gpt-3.5-turbo"  # Cheaper but less capable
```

### Custom Client Configuration

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    organization="org-xxx"  # Optional: for organization accounts
)
```

---

## Monitoring & Analytics

### Track API Usage

```python
from datetime import datetime

start_tokens = 0  # Track from OpenAI dashboard
end_tokens = 0    # Check after queries

cost = (end_tokens - start_tokens) * 0.000015  # gpt-4-mini input rate
print(f"Cost: ${cost:.4f}")
```

### Log All Requests

Add to your code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Support & Resources

- **OpenAI Docs:** https://platform.openai.com/docs
- **API Reference:** https://platform.openai.com/docs/api-reference
- **Pricing:** https://openai.com/pricing
- **Status:** https://status.openai.com/

---

## Migration Notes

### Changed from Anthropic Claude to OpenAI GPT-4

Files updated:
- ✅ `utils/llm_client.py` - Client initialization
- ✅ `requirements.txt` - Dependencies
- ✅ `.env.example` - Environment variable
- ✅ All workflow nodes - API calls
- ✅ All agent files - Response parsing
- ✅ Documentation - References

### Behavior Differences

| Aspect | Anthropic | OpenAI |
|--------|-----------|--------|
| Response access | `response.content[0].text` | `response.choices[0].message.content` |
| Model name | claude-sonnet-4-6 | gpt-4-mini |
| Cost | ~2x more expensive | ~2x cheaper |
| Speed | Slightly slower | Fast responses |
| Quality | Excellent | Excellent |

---

## Questions?

Check the files:
- STUDENT_ASSIGNMENTS.md - Student setup
- README.md - Project overview
- WORKFLOW_GUIDE.md - Agent development

Or run: `python main.py` to see everything in action!
