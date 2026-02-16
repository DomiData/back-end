from app.utils.logger import logger
from collections import defaultdict
from app.repository.occurrence import OccurrenceRepository
from app.schema.requests import (
    CityReportRequest,
    DiseaseReportByCityRequest,
    DiseaseReportByStateRequest,
    StateReportRequest,
)


class ReportService:
    def __init__(self, occurrence_repository: OccurrenceRepository):
        self.occ_repo = occurrence_repository

    async def generate_city_report(self, request: CityReportRequest):
        logger.info(
            "Generating city report for city_code={%s}, start_date={%s}, end_date={%s}",
            request.city_code,
            request.start_date,
            request.end_date,
        )
        stats = await self.occ_repo.get_city_report(
            city_code=request.city_code,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        report = defaultdict(dict)
        for health_unit_name, disease, total in stats:
            report[health_unit_name][disease] = total
        return report

    async def generate_disease_report_by_city(
        self, request: DiseaseReportByCityRequest
    ):
        logger.info(
            "Generating disease report by city for city_code={%s}, disease={%s}, start_date={%s}, end_date={%s}",
            request.city_code,
            request.disease_acronym,
            request.start_date,
            request.end_date,
        )
        stats = await self.occ_repo.get_disease_report_by_city(
            city_code=request.city_code,
            disease=request.disease_acronym,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        report = defaultdict(dict)
        for health_unit_name, total in stats:
            report[health_unit_name] = total
        return report

    async def generate_disease_report_by_state(
        self, request: DiseaseReportByStateRequest
    ):
        logger.info(
            "Generating disease report by state for state_code={%s}, disease={%s}, start_date={%s}, end_date={%s}",
            request.state_code,
            request.disease_acronym,
            request.start_date,
            request.end_date,
        )
        stats = await self.occ_repo.get_disease_report_by_state(
            state_code=request.state_code,
            disease=request.disease_acronym,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        report = defaultdict(dict)
        for city_id, total in stats:
            report[city_id] = total
        return report

    async def generate_state_report(self, request: StateReportRequest):
        logger.info(
            "Generating state report for state_code={%s}, start_date={%s}, end_date={%s}",
            request.state_code,
            request.start_date,
            request.end_date,
        )
        stats = await self.occ_repo.get_state_report(
            state_code=request.state_code,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        report = defaultdict(dict)
        for city_id, disease, total in stats:
            report[city_id][disease] = total
        return report
