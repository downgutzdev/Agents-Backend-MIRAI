# config.py
'''BASE_URL = "https://7c0728d3ec38.ngrok-free.app"

AGENT_URLS = {
    "natural_agent": f"{BASE_URL}/mirai_agents/natural/ask",
    "guardrails":    f"{BASE_URL}/mirai_agents/guardrails/ask",
    "planner":       f"{BASE_URL}/mirai_agents/planner/ask",
    "professor":     f"{BASE_URL}/mirai_agents/professor/ask",
    "schema_creator":f"{BASE_URL}/mirai_agents/schema_creator/ask",
}
'''

BASE_URL = "http://127.0.0.1:9200"

AGENT_URLS = {
    "natural_agent": f"{BASE_URL}/mirai_agents/natural/ask",
    "guardrails": f"{BASE_URL}/mirai_agents/guardrails/ask",
    "planner": f"{BASE_URL}/mirai_agents/planner/ask",
    "professor": f"{BASE_URL}/mirai_agents/professor/ask",
    "schema_creator": f"{BASE_URL}/mirai_agents/schema_creator/ask",
}
