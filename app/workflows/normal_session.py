import sys
from pathlib import Path
import requests

# ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from config import AGENT_URLS
from app.utils.session_store import save_session_message


def call_agent(url: str, payload: dict):
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def run_natural_session(session_id: str, question: str):
    """
    Workflow for natural conversation:
    - Calls NaturalAgent
    - Saves history in Redis
    """
    # 1️⃣ Call Natural Agent directly
    natural_payload = {
        "question": question,
        "model_name": "gemini-1.5-flash",
        "temperature": 0.4,
    }
    natural_resp = call_agent(AGENT_URLS["natural_agent"], natural_payload)

    # 2️⃣ Save history in Redis
    save_session_message(session_id, role="user", content=question)
    save_session_message(session_id, role="agent", content=natural_resp.get("answer"))

    return {"status": "ok", "answer": natural_resp.get("answer")}


if __name__ == "__main__":
    session_id = "test_session_natural"
    question = input("Type your question: ").strip()

    result = run_natural_session(session_id, question)
    print("\n--- RESULT ---")
    print(result)
