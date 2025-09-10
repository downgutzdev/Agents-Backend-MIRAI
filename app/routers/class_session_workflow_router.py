from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.workflows.class_session import run_class_session, finalize_session_with_plan

router = APIRouter(prefix="/workflows/class-session", tags=["workflows/class-session"])

class ClassRunRequest(BaseModel):
    user_text: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    student_uuid: str = Field(..., min_length=36)

class ClassRunResponse(BaseModel):
    status: str
    planner: Optional[Dict[str, Any]] = None
    professor: Optional[Dict[str, Any]] = None

@router.post("/run", response_model=ClassRunResponse, status_code=status.HTTP_200_OK)
def run(req: ClassRunRequest):
    """
    Runs a class session workflow: Planner + Teacher.
    """
    try:
        out = run_class_session(aluno_uuid=req.student_uuid, question=req.user_text, session_id=req.session_id)
        return {"status": "ok", "planner": out.get("planner"), "professor": out.get("professor")}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Class session workflow failed: {e}")

class ClassFinalizeRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    student_uuid: str = Field(..., min_length=36)

class ClassFinalizeResponse(BaseModel):
    status: str
    sessao_uuid: Optional[str] = None   # kept as-is for DB consistency
    avaliacao: Optional[Dict[str, Any]] = None  # kept as-is
    plano: Optional[str] = None         # kept as-is

@router.post("/finalize", response_model=ClassFinalizeResponse, status_code=status.HTTP_200_OK)
def finalize(req: ClassFinalizeRequest):
    """
    Finalizes a class session: aggregates evaluation + saves plan in DB.
    """
    try:
        out = finalize_session_with_plan(aluno_uuid=req.student_uuid, session_id=req.session_id)
        return out
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Finalize workflow failed: {e}")
