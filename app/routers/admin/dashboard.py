from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_admin_user
from app.services.stats import get_dashboard_stats, get_recent_orders, get_sales_chart_data

router = APIRouter(prefix="/admin", tags=["admin-dashboard"])


@router.get("")
async def dashboard(
    request: Request,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """관리자 대시보드"""
    stats = get_dashboard_stats(session)
    recent_orders = get_recent_orders(session)
    chart_data = get_sales_chart_data(session)

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "stats": stats,
            "recent_orders": recent_orders,
            "chart_data": chart_data
        }
    )
