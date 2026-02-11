import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.health_unit import HealthUnit
from app.utils.logger import logger

async def load_cnes_csv(db: AsyncSession, csv_path: str):
    logger.info(f"Starting CNES data load")
    df_cnes = pd.read_csv(
        csv_path,
        sep=';',
        dtype={
        'CO_CNES': str,
        'CO_MUNICIPIO_GESTOR': str,
        'TP_UNIDADE': str
        }
    ).fillna('')
    for ind, row in df_cnes.iterrows():
        try:
            cnes_code = row['CO_CNES'].zfill(7)
            query = select(HealthUnit).where(HealthUnit.cnes_code == cnes_code)

            health_unit = await db.execute(query)
            exists = health_unit.scalar_one_or_none()
            if exists:
                continue

            logger.debug(f"Adding new Health Unit: {row['NO_FANTASIA']} ({cnes_code})")

            new_unit = HealthUnit(
                cnes_code=cnes_code,
                name=row['NO_FANTASIA'],
                district=row['NO_BAIRRO'],
                city_code=row['CO_MUNICIPIO_GESTOR'],
                unit_type=row['TP_UNIDADE'],
                latitude=row['NU_LATITUDE'],
                longitude=row['NU_LONGITUDE']
            )
            db.add(new_unit)
        except Exception as e:
            logger.error(f"Failed to load CNES data in {ind}: {str(e)} ")
            continue

    await db.commit()
    logger.info("CNES load finished.")
