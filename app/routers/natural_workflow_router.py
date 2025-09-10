from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from app.workflows.normal_session import run_natural_session

router = APIRouter(prefix="/workflows/natural", tags=["workflows/natural"])

class NaturalRunRequest(BaseModel):
    user_text: str = Field(..., min_length=1)
    session_id: Optional[str] = None

class NaturalRunResponse(BaseModel):
    status: str
    answer: Optional[str] = None

@router.post("/run", response_model=NaturalRunResponse, status_code=status.HTTP_200_OK)
def run(req: NaturalRunRequest):
    """
    Runs the natural conversation workflow (NaturalAgent).
    """
    try:
        out = run_natural_session(session_id=req.session_id or "session_default", question=req.user_text)
        return {"status": "ok", "answer": out.get("answer")}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Natural workflow failed: {e}")
