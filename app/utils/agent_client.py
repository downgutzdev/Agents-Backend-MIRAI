# app/utils/agent_client.py
from typing import Any, Dict
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import AGENT_URLS

AGENT_DEBUG   = os.getenv("AGENT_DEBUG", "0") == "1"
AGENT_TIMEOUT = float(os.getenv("AGENT_TIMEOUT", "60"))

_session = requests.Session()
_retry = Retry(
    total=5,
    backoff_factor=0.8,
    status_forcelist=[502, 503, 504],
    allowed_methods=["GET", "POST"],
    raise_on_status=False,
)
_adapter = HTTPAdapter(max_retries=_retry, pool_maxsize=10, pool_block=False)
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)

def post_agent(agent_key: str, payload: Dict[str, Any], timeout: float | None = None) -> Dict[str, Any]:
    url = AGENT_URLS.get(agent_key)
    if not url:
        raise ValueError(f"AGENT_URLS sem entrada para '{agent_key}'")
    t = timeout or AGENT_TIMEOUT
    headers = {"Connection": "close"}  # ngrok gosta disso
    if AGENT_DEBUG:
        print(f"[agent_client] POST {url} timeout={t} payload={payload}")
    resp = _session.post(url, json=payload, timeout=t, headers=headers)
    if AGENT_DEBUG:
        print(f"[agent_client] <- {resp.status_code} {resp.text[:500]}")
    if 500 <= resp.status_code <= 599:
        raise requests.HTTPError(
            f"{resp.status_code} Server Error at {url}\nResponse: {resp.text}",
            response=resp
        )
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        # inclui corpo no erro para debug de 4xx (ex.: 422)
        raise requests.HTTPError(f"{e}\nResponse body: {resp.text}", response=resp) from e
    return resp.json()
