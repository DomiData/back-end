from typing import Union
from fastapi import FastAPI

from app.core.database import create_db, SessionLocal
from app.core.config import settings

from app.etl.main_etl import run_complete_etl
from app.utils.logger import logger
from app import model
async def lifespan(app: FastAPI):
    await create_db()
    if settings.POPULATE_DB:
        async with SessionLocal() as session:
            logger.warning("Database populated with data!")
            await run_complete_etl(session)
    yield
    # Shutdown code here

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
