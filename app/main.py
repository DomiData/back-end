from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_db
from app.core.firebase import initialize_firebase_app
from app.core.config import settings
from app.api.user import router as user_router

async def lifespan(app: FastAPI):
    await create_db()
    initialize_firebase_app()
    yield
    # Shutdown code here

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

@app.get("/")
def read_root():
    return {"Hello": "World"}
