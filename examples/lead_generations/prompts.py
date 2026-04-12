from models import AgentResult

SYSTEM_PROMPT: str = f"""\
## OUTPUT

Wrap your output in a JSON code block (```json ... ```). The JSON must validate against this schema:

```json
{AgentResult.model_json_schema()}
```
"""
