import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_demo_token
from app.db.session import get_db
from app.domains.dashboard import service
from app.domains.dashboard.schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(require_demo_token)])


@router.get("/stats", response_model=DashboardStats)
async def dashboard_stats(
    patient_id: uuid.UUID, days: int = Query(default=30, ge=1, le=365), db: AsyncSession = Depends(get_db)
):
    """Backs the AI Call Center's stat cards and response-breakdown chart."""
    return await service.get_dashboard_stats(db, patient_id=patient_id, days=days)
