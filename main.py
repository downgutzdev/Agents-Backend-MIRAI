from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.natural_workflow_router import router as natural_router
from app.routers.class_session_workflow_router import router as class_router
from app.routers.analytics_workflow_router import router as analytics_router
from app.routers.pipeline_router import router as pipeline_router

app = FastAPI(title="Workflow Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(natural_router)
app.include_router(class_router)
app.include_router(analytics_router)
app.include_router(pipeline_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=9300, reload=True)
