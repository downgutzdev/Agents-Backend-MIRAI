from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.workflows.generate_query import run_generate_query

router = APIRouter(prefix="/workflows/analytics", tags=["workflows/analytics"])

class AnalyticsQueryRequest(BaseModel):
    user_text: str = Field(..., min_length=1)
    user_uuid: str = Field(..., min_length=36)
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AnalyticsQueryResponse(BaseModel):
    status: str
    kind: Optional[str] = None
    columns: Optional[List[str]] = None
    rows: Optional[List[List[Any]]] = None
    meta: Optional[Dict[str, Any]] = None

@router.post("/query", response_model=AnalyticsQueryResponse, status_code=status.HTTP_200_OK)
def query(req: AnalyticsQueryRequest):
    try:
        ctx = req.context or {}
        ctx["user_uuid"] = req.user_uuid   # garante presença
        out = run_generate_query(question=req.user_text, session_id=req.session_id, context=ctx)
        return out
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Analytics workflow failed: {e}")
