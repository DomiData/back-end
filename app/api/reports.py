from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_report_service
from app.utils.logger import logger
from app.services.report import ReportService
from app.schema.requests import (
    DiseaseReportByCityRequest,
    CityReportRequest,
    DiseaseReportByStateRequest,
    StateReportRequest,
)

# User Role = "admin" or "health_department" can access these endpoints
router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/city")
async def get_city_report(
    request: CityReportRequest,
    report_service: ReportService = Depends(get_report_service),
):
    try:
        report = await report_service.generate_city_report(request=request)
        return report
    except Exception as e:
        logger.error("Error generating city report: %s", e)
        raise HTTPException(
            status_code=500, detail="Error generating city report"
        ) from e


@router.post("/city/disease")
async def get_disease_report_by_city(
    request: DiseaseReportByCityRequest,
    report_service: ReportService = Depends(get_report_service),
):
    try:
        report = await report_service.generate_disease_report_by_city(request)
        return report
    except Exception as e:
        logger.error("Error generating disease report by city: %s", e)
        raise HTTPException(
            status_code=500, detail="Error generating disease report by city"
        ) from e


@router.post("/state/disease")
async def get_disease_report_by_state(
    request: DiseaseReportByStateRequest,
    report_service: ReportService = Depends(get_report_service),
):
    try:
        report = await report_service.generate_disease_report_by_state(request)
        return report
    except Exception as e:
        logger.error("Error generating disease report by state: %s", e)
        raise HTTPException(
            status_code=500, detail="Error generating disease report by state"
        ) from e


@router.post("/state")
async def get_state_report(
    request: StateReportRequest,
    report_service: ReportService = Depends(get_report_service),
):
    try:
        report = await report_service.generate_state_report(request)
        return report
    except Exception as e:
        logger.error("Error generating state report: %s", e)
        raise HTTPException(
            status_code=500, detail="Error generating state report"
        ) from e
