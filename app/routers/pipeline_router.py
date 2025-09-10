from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.workflows.guardrails_runner import handle_user_message

router = APIRouter(prefix="/workflows/pipeline", tags=["workflows/pipeline"])

class PipelineMessageRequest(BaseModel):
    user_text: str = Field(..., min_length=1)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@router.post("/message", status_code=status.HTTP_200_OK)
def message(req: PipelineMessageRequest):
    """
    Orchestrates the full pipeline:
    Guardrails → Trigger → Corresponding workflow.
    """
    try:
        out = handle_user_message(
            user_text=req.user_text,
            context=req.context or {},
            user_id=req.user_id,
            session_id=req.session_id,
        )
        return out
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Pipeline failed: {e}")
