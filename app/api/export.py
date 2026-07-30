from fastapi import Depends, APIRouter, Response
from app.schema.export import ExportDashboardData, ExportHeatmapData
from app.services.export.export import ExportService
from app.utils.util import secure_filename
from app.api.deps import get_export_service
from app.core.security import get_firebase_claims

router = APIRouter(
    prefix="/export",
    tags=["Export"],
    dependencies=[Depends(get_firebase_claims)],
)


def build_export_response(
    content: bytes, media_type: str, file_name: str, export_format: str
):
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={file_name}.{export_format}",
            "Cache-Control": "no-cache",
        },
    )


@router.post("/dashboard")
async def export_dashboard(
    request: ExportDashboardData,
    service: ExportService = Depends(get_export_service),
):
    content, media_type = await service.export_dashboard(request)
    return build_export_response(
        content, media_type, secure_filename(request.file_name), request.export_format
    )


@router.post("/heatmap")
async def export_heatmap(
    request: ExportHeatmapData,
    service: ExportService = Depends(get_export_service),
):
    content, media_type = await service.export_heatmap_data(request)
    return build_export_response(
        content, media_type, secure_filename(request.file_name), request.export_format
    )
