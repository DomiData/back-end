from app.services.export.csv_strategy import CSVStrategy
from app.services.export.excel_strategy import ExcelStrategy
from typing import List


class ExportContext:
    _strategies = {"csv": CSVStrategy(), "xlsx": ExcelStrategy()}

    @classmethod
    async def execute(cls, export_format: str, data: List[dict]):
        strategy = cls._strategies.get(export_format.lower())
        if not strategy:
            raise ValueError(f"Format {export_format} not supported")
        content = await strategy.export(data)
        return content, strategy.media_type
