import asyncio
from pathlib import Path

import pandas as pd
from pysus.api.ftp.client import FTP  # type: ignore
from pysus.api.ftp.databases import SINAN  # type: ignore

from app.utils.logger import logger


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def normalize_pysus_return(raw_data):
    try:
        if hasattr(raw_data, "to_dataframe"):
            return raw_data.to_dataframe()
        elif isinstance(raw_data, pd.DataFrame):
            return raw_data
        elif isinstance(raw_data, list):
            df_list = []
            for item in raw_data:
                if hasattr(item, "to_dataframe"):
                    df_list.append(item.to_dataframe())
                elif isinstance(item, pd.DataFrame):
                    df_list.append(item)

            if df_list:
                return pd.concat(df_list, ignore_index=True)

    except Exception as e:
        logger.error(f"Error during PySUS data normalization: {e}")

    return pd.DataFrame()


def get_disease_list():
    try:
        logger.info("Loading SINAN metadata...")
        return SINAN.model_fields["group_definitions"].default
    except Exception as e:
        logger.warning(f"Metadata offline or unreachable ({e}). Using fallback list.")
        return {
            "DENG": "Dengue",
            "CHIK": "Chikungunya",
            "ZIKA": "Zika",
            "ANIM": "Animais_Peconhentos",
            "IEXO": "Intoxicacao_Exogena",
            "LEIV": "Leishmaniose_Visceral",
        }


async def _download_raw_data(acronym, year):
    client = FTP()
    await client.login()

    try:
        dataset = SINAN(client=client)
        files = await dataset.search(year=int(year))
        matches = [
            file
            for file in files
            if file.group is not None and file.group.name == acronym
        ]

        if not matches:
            logger.warning(f"No SINAN file found for {acronym} in {year}.")
            return pd.DataFrame()

        remote_file = sorted(
            matches,
            key=lambda file: "PRELIM" in str(file.path).upper(),
        )[0]
        cache_dir = PROJECT_ROOT / "data" / "raw" / "pysus_cache"
        local_file = await remote_file.download(output=cache_dir)
        return await local_file.load()
    finally:
        await client.close()


def download_raw_data(acronym, year):
    logger.info(f"Downloading data for {acronym} (Year: {year})...")
    try:
        raw_data = asyncio.run(_download_raw_data(acronym, year))
        df = normalize_pysus_return(raw_data)

        if df.empty:
            logger.warning(
                f"Download finished but no records were found for {acronym} in {year}."
            )
        return df
    except Exception as e:
        if "No objects to concatenate" in str(e):
            logger.warning(
                f"No data available for {acronym} in {year} (PySUS Empty Return)."
            )
            return pd.DataFrame()
        logger.error(f"Failed to download {acronym}: {e}")
        return pd.DataFrame()
