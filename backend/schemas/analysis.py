from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=500, description="Name of the product to analyze")


class AnalysisStatus(BaseModel):
    job_id: str
    status: str
    current_agent: str | None = None
    progress: float = 0.0


class SWOTItem(BaseModel):
    category: str
    point: str
    confidence: float = 0.0
    citations: list[str] = []


class AnalysisResult(BaseModel):
    job_id: str
    product_name: str
    swot: list[SWOTItem] = []
    summary: str = ""
    competitors: list[str] = []
    report_markdown: str = ""
