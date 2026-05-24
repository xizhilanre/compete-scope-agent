from fastapi import APIRouter

router = APIRouter(tags=["analyze"], prefix="/analyze")


@router.post("/start")
async def start_analysis():
    """Start a new competitive analysis job. Returns job_id for SSE polling."""
    return {"job_id": "placeholder", "status": "queued"}


@router.get("/{job_id}/status")
async def job_status(job_id: str):
    """Get current status and intermediate results for a job."""
    return {"job_id": job_id, "status": "running", "current_agent": "Research"}
