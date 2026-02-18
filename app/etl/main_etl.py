from sqlalchemy.ext.asyncio import AsyncSession
from app.etl.loader.disease_loader import seed_diseases
from app.etl.loader.cnes_loader import load_cnes_csv
from app.etl.loader.occurrence_loader import load_sinan_occurrences
from app.etl.etl_sinan import main as run_elt_sinan
from app.etl.etl_cnes import main as run_elt_cnes
from app.utils.logger import logger
import os


async def run_complete_etl(db: AsyncSession):
    logger.info("Starting LOAD ETL process")

    run_elt_cnes()
    run_elt_sinan()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

    CNES_CSV_FILE = os.path.join(PROJECT_ROOT, "cnes", "CNES_PB_MAP.csv")
    SINAN_PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

    await seed_diseases(db)
    await load_cnes_csv(db, CNES_CSV_FILE)
    await load_sinan_occurrences(db, SINAN_PROCESSED_DIR)

    logger.info("ETL process completed successfully")
