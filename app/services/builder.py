from sqlalchemy.orm import Session
from app.model import Occurrence, Disease, HealthUnit
from app.model.heatmap_input import HeatmapQueryInput

class HeatMapQueryBuilder:
    def __init__(self, session: Session):
        self.session = session
        self.query = session.query(Occurrence)

    def build(self, params: HeatmapQueryInput):
        self._apply_filters(params)
        self._apply_group_by(params)
        self._apply_metric(params)
        return self.query.all()

    def _apply_filters(self, params: HeatmapQueryInput):
        pass

    def _apply_group_by(self, params: HeatmapQueryInput):
        pass

    def _apply_metric(self, params: HeatmapQueryInput):
        pass
