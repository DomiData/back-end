from io import BytesIO
from typing import List
import pandas as pd
from app.services.export.export_strategy import ExportStrategy


class ExcelStrategy(ExportStrategy):
    async def export(self, data: List[dict]):
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    @property
    def media_type(self):
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
