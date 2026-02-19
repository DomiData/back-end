from pydantic import BaseModel


class DashboardBuilderOutput(BaseModel):
    label: str
    value: int
