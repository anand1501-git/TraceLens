from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.service import analyze_traceback


PROJECT_ROOT = Path(__file__).resolve().parent
app = FastAPI(title="TraceLens API")


class AnalysisRequest(BaseModel):
    traceback: str = Field(min_length=1, max_length=100_000)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(request: AnalysisRequest):
    if not request.traceback.strip():
        raise HTTPException(
            status_code=422,
            detail="Traceback must not be blank."
        )

    return analyze_traceback(request.traceback, PROJECT_ROOT)
