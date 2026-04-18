import re

pattern = r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+|UNION\s+SELECT|--\s|;\s*$)"
query = "what menu available?"

match = re.search(pattern, query, re.IGNORECASE)

print(match)