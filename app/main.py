from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.database import create_db, SessionLocal, get_db
from app.core.firebase import initialize_firebase_app
from app.core.config import settings
from app.api.user import router as user_router
from app.etl.main_etl import run_complete_etl
from app.model.heatmap_builder import HeatmapQueryBuilderInput
from app.services.builder import HeatMapQueryBuilder
from app.utils.logger import logger
from app.schema.requests import NaturalSearchRequest
from app.services.parser import QueryIntentParser, get_query_intent_parser

async def lifespan(app: FastAPI):
    await create_db()
    initialize_firebase_app()
    if settings.POPULATE_DB:
        async with SessionLocal() as session:
            logger.warning("Database populated with data!")
            await run_complete_etl(session)
    yield

origins = [
    settings.FRONTEND_URL
]

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router)

@app.post("/heatmap")
async def heatmap(
    params: HeatmapQueryBuilderInput,
    session: Session = Depends(get_db)
):
    query_builder = HeatMapQueryBuilder(session)
    result = await query_builder.build(params)
    return result

@app.post("/heatmap/natural-search")
async def natural_search(
    request: NaturalSearchRequest,
    session: AsyncSession = Depends(get_db),
    parser: QueryIntentParser = Depends(get_query_intent_parser)
):
    params = await parser.transform(natural_query=request.query)
    query_builder = HeatMapQueryBuilder(session)
    result = await query_builder.build(params)
    return result