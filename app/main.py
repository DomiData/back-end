from fastapi import FastAPI
from .core.database import create_db
from .core.firebase import initialize_firebase_app

async def lifespan(app: FastAPI):
    await create_db()
    initialize_firebase_app()
    yield
    # Shutdown code here

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}
