from pysus.online_data.SINAN import download  # type: ignore
from pysus.ftp.databases.sinan import SINAN  # type: ignore
import pandas as pd
from app.utils.logger import logger


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
        logger.info("Connecting to SINAN metadata...")
        sinan_metadata = SINAN().load()
        return sinan_metadata.diseases
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


def download_raw_data(acronym, year):
    logger.info(f"Downloading data for {acronym} (Year: {year})...")
    try:
        raw_data = download(diseases=acronym, years=year)
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
