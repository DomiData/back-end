from abc import ABC, abstractmethod
from typing import List


class ExportStrategy(ABC):
    @abstractmethod
    async def export(self, data: List[dict]):
        pass

    @property
    @abstractmethod
    def media_type(self) -> str:
        pass
