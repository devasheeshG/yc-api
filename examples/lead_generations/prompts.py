from models import AgentResult

SYSTEM_PROMPT: str = f"""\
## OUTPUT FORMAT

{AgentResult.model_json_schema()}
"""
