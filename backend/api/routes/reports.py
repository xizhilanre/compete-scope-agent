"""Report routes -- read generated competitive analysis reports.

Endpoints are wired to the real database layer.
"""

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.crud import get_report
from backend.db.database import get_db
from backend.schemas.base import err
from backend.schemas.base import ok
from backend.schemas.report import ReportResponse

router = APIRouter(tags=["reports"], prefix="/reports")


@router.get("/{report_id}")
async def get_report_route(report_id: str, db: AsyncSession = Depends(get_db)):
    """Get a structured analysis report by its hex ID."""
    report = await get_report(db, report_id)
    if not report:
        return err("报告不存在")
    return ok(ReportResponse.model_validate(report))
