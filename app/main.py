from typing import Union
from fastapi import Depends, FastAPI
from app.core.database import create_db, SessionLocal, get_db
from app.core.config import settings
from app.etl.main_etl import run_complete_etl
from app.model.heatmap_input import HeatmapQueryInput
from app.services.builder import HeatMapQueryBuilder
from app.utils.logger import logger
from sqlalchemy.orm import Session

async def lifespan(app: FastAPI):
    await create_db()
    if settings.POPULATE_DB:
        async with SessionLocal() as session:
            logger.warning("Database populated with data!")
            await run_complete_etl(session)
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}
    

@app.post("/heatmap")
async def heatmap(
    params: HeatmapQueryInput,
    session: Session = Depends(get_db)
):
    query_builder = HeatMapQueryBuilder(session)
    return await query_builder.build(params)
