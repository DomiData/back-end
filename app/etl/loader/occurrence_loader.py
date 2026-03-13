import pandas as pd
import glob
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.occurrence import Occurrence
from app.model.health_unit import HealthUnit
from app.utils.logger import logger


async def load_sinan_occurrences(db: AsyncSession, processed_dir: str):
    logger.info("Scanning directory for SINAN data")
    csv_files = glob.glob(os.path.join(processed_dir, "*.csv"))

    query = await db.execute(select(HealthUnit.cnes_code))
    valid_cnes = set(query.scalars().all())

    if not csv_files:
        logger.warning(f"No CSV files found in {processed_dir}")
        return

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        disease_acronym = file_name.split("_")[0]

        logger.info(f"Processing file: {file_name} for disease: {disease_acronym}")
        df = pd.read_csv(
            file_path,
            sep=";",
            dtype={"ID_UNIDADE": str, "ID_MUNICIP": str, "EVOLUCAO": str},
        ).fillna("")

        for ind, row in df.iterrows():
            try:
                cnes_id = str(row["ID_UNIDADE"]).zfill(7)

                if cnes_id not in valid_cnes:
                    logger.warning(
                        f"Invalid CNES ID {cnes_id} at row {ind} in {file_name}, skipping."
                    )
                    continue
                occurrence = Occurrence(
                    disease_type=disease_acronym,
                    health_unit_id=cnes_id,
                    notification_date=pd.to_datetime(row["DT_NOTIFIC"]).date(),
                    city_id=str(row["ID_MUNICIP"]).zfill(7),
                    patient_age=row["NU_IDADE_N"],
                    evolution=row["EVOLUCAO"],
                    patient_sex=row["CS_SEXO"],
                )
                db.add(occurrence)

            except Exception as e:
                logger.error(f"Failed to process {ind} in {file_name}: {str(e)}")
                continue

        await db.commit()
        logger.info(f"Successfully loaded occurrences from {file_name}")
