from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.firebase import initialize_firebase_app
from app.core.config import settings
from app.core.security import get_firebase_claims
from app.api.user import router as user_router
from app.api.chat import router as chat_router
from app.api.export import router as export_router
from app.api.health import router as health_router
from app.schema.builder import HeatmapBuilderInput
from app.schema.builder.dashboard_input import DashboardBuilderInput
from app.repository.query.dashboard_builder import DashboardQueryBuilder
from app.repository.query.heatmap_builder import HeatMapQueryBuilder
from app.schema.requests import NaturalSearchRequest
from app.services.parser import QueryIntentParser, get_query_intent_parser


async def lifespan(app: FastAPI):
    initialize_firebase_app()
    yield


origins = [settings.FRONTEND_URL]

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(export_router)
app.include_router(health_router)


@app.post("/heatmap")
async def heatmap(params: HeatmapBuilderInput, session: AsyncSession = Depends(get_db)):
    query_builder = HeatMapQueryBuilder(session)
    result = await query_builder.build(params)
    return result


@app.post("/dashboard")
async def dashboard(
    params: DashboardBuilderInput,
    session: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_firebase_claims),
):
    query_builder = DashboardQueryBuilder(session)
    result = await query_builder.build(params)
    return result


@app.post("/heatmap/natural-search")
async def natural_search(
    request: NaturalSearchRequest,
    session: AsyncSession = Depends(get_db),
    parser: QueryIntentParser = Depends(get_query_intent_parser),
):
    params = await parser.transform(natural_query=request.query)
    query_builder = HeatMapQueryBuilder(session)
    result = await query_builder.build(params)
    return result
