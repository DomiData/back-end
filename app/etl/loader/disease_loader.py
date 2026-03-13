from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.disease import Disease
from app.utils.logger import logger
from app.etl.downloader.sinan_downloader import get_disease_list


async def seed_diseases(db: AsyncSession):
    logger.info("Starting SINAN disease metadata seed")

    try:
        sinan_diseases = get_disease_list()

        if not sinan_diseases:
            logger.error("Failed to fetch disease list from SINAN metadata")
            return

        for acronym, name in sinan_diseases.items():
            query = select(Disease).where(Disease.acronym == acronym)
            result = await db.execute(query)
            db_disease = result.scalar_one_or_none()

            if not db_disease:
                logger.debug(f"Registering new disease: {acronym} - {name}")
                disease = Disease(acronym=acronym, name=name)
                db.add(disease)

        await db.commit()
        logger.info("Disease seed completed successfully.")

    except Exception as e:
        logger.error(f"Unexpected error during disease seeding: {str(e)}")
        await db.rollback()
        raise
