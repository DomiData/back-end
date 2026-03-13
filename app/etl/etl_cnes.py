import os
from app.etl.downloader.cnes_downloader import download_raw_cnes
from app.etl.cleaner.cnes_cleaner import process_cnes_data
from app.utils.logger import logger


def main():
    STATE_CODE_PB = "25"
    TARGET_COLUMNS = [
        "CO_CNES",  # Unique ID for the health unit
        "NO_FANTASIA",  # Trading name of the post
        "NU_LATITUDE",  # Critical for the map
        "NU_LONGITUDE",  # Critical for the map
        "CO_MUNICIPIO_GESTOR",  # City code
        "TP_UNIDADE",  # Type of unit (to filter only primary care)
        "NO_BAIRRO",  # Neighborhood for local insights
    ]

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

    RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
    PROCESSED_DIR = os.path.join(PROJECT_ROOT, "cnes")

    for directory in [RAW_DIR, PROCESSED_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")

    logger.info("Starting CNES (Health Units) ETL process...")

    try:
        logger.info("Attempting to download raw CNES database...")
        raw_file_path = download_raw_cnes(RAW_DIR)

        if not raw_file_path or not os.path.exists(raw_file_path):
            logger.error("Raw CNES file not found or download failed.")
            return

        logger.info(f"Processing CNES data for State: {STATE_CODE_PB}")
        df_cleaned = process_cnes_data(raw_file_path, STATE_CODE_PB, TARGET_COLUMNS)

        if df_cleaned.empty:
            logger.warning("Cleaning process returned an empty dataset for CNES.")
        else:
            final_path = os.path.join(PROCESSED_DIR, "CNES_PB_MAP.csv")
            df_cleaned.to_csv(final_path, sep=";", index=False)
            logger.info(
                f"Successfully saved {len(df_cleaned)} health units to {final_path}"
            )

    except Exception as e:
        logger.error(f"Critical error during CNES ETL: {str(e)}")

    logger.info("CNES ETL process finished.")


if __name__ == "__main__":
    main()
