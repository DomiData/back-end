from typing import List
import pandas as pd
from app.services.export.export_strategy import ExportStrategy


class CSVStrategy(ExportStrategy):
    async def export(self, data: List[dict]):
        df = pd.DataFrame(data)
        return df.to_csv(index=False)

    @property
    def media_type(self):
        return "text/csv"
