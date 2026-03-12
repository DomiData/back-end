import os
from app.etl.downloader.sinan_downloader import download_raw_data, get_disease_list
from app.etl.cleaner.sinan_cleaner import filter_state_and_columns
from app.utils.logger import logger
import pandas as pd

def main():
    STATE_CODE_PB = "25"

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
    RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
    PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

    for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Directory created: {directory}")

    MANDATORY = [
        "DT_NOTIFIC",
        "ID_UNIDADE",
        "ID_MUNICIP",
        "ID_MN_RESI",
    ]  # DATA, O Posto de Saúde, Município
    OPTIONAL = ["NU_IDADE_N", "CS_SEXO", "EVOLUCAO"]
    disease_list = get_disease_list()

    for YEAR in range(2023, 2027):

        logger.info(f"Starting ETL process for year {YEAR}")

        acronyms_to_skip = {"ACBI", "ACGR", "ANIM", "MENT", "PAIR", "VIOL"}
        for acronym, name in disease_list.items():

            if acronym == "DENG" and YEAR == 2024:
                raw_df_file = RAW_DATA_DIR + "/DENG_2024.csv"
                raw_df = pd.read_csv(raw_df_file, sep=";")
                processed_df = filter_state_and_columns(
                    raw_df, STATE_CODE_PB, MANDATORY, OPTIONAL
                )

                if processed_df.empty:
                    logger.info(
                        f"National data downloaded for {acronym}, but no cases found for PB"
                    )
                    continue

                processed_file_path = os.path.join(
                    PROCESSED_DATA_DIR, f"{acronym}_{YEAR}_PB.csv"
                )
                processed_df.to_csv(processed_file_path, sep=";", index=False)
                logger.info(
                    f"Successfully processed {len(processed_df)} cases for {acronym} in PB"
                )

                del raw_df
                del processed_df
                continue
            if acronym in acronyms_to_skip:
                logger.info(f"Skipping disease: {name} ({acronym})")
                continue

            logger.info(f"Processing disease: {name} ({acronym})")

            try:
                raw_df = download_raw_data(acronym, YEAR)

                if raw_df.empty:
                    logger.warning(f"No data returned for {acronym} in {YEAR}")
                    continue

                raw_file_path = os.path.join(RAW_DATA_DIR, f"{acronym}_{YEAR}.csv")
                raw_df.to_csv(raw_file_path, sep=";", index=False)
                logger.debug(f"Raw data saved to {raw_file_path}")

                processed_df = filter_state_and_columns(
                    raw_df, STATE_CODE_PB, MANDATORY, OPTIONAL
                )

                if processed_df.empty:
                    logger.info(
                        f"National data downloaded for {acronym}, but no cases found for PB"
                    )
                    continue

                processed_file_path = os.path.join(
                    PROCESSED_DATA_DIR, f"{acronym}_{YEAR}_PB.csv"
                )
                processed_df.to_csv(processed_file_path, sep=";", index=False)
                logger.info(
                    f"Successfully processed {len(processed_df)} cases for {acronym} in PB"
                )

                del raw_df
                del processed_df
            except Exception as e:
                logger.error(f"Critical error processing {acronym}: {str(e)}")

    logger.info("ETL process finished.")


if __name__ == "__main__":
    main()
