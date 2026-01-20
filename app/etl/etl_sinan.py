import os
from app.etl.downloader.sinan_downloader import download_raw_data, get_disease_list
from app.etl.cleaner.sinan_cleaner import filter_state_and_columns
from app.utils.logger import logger

def main():
    YEAR = 2025
    STATE_CODE_PB = '25'

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))    
    PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
    RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
    PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
    
    for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Directory created: {directory}")
        
    TARGET_COLUMNS = [
    'DT_NOTIFIC', 'DT_SIN_PRI', 'DT_OCORR', # Datas possíveis
    'ID_MUNICIP', 'ID_MUNICIP_NOTIFICACAO', # Local da Notificação
    'ID_UNIDADE', 'ID_UNIT',                # O Posto de Saúde (Crucial)
    'ID_MN_RESI',                           # Onde Mora
    'NU_IDADE_N', 'CS_SEXO',                # Perfil
    'CLASSI_FIN', 'EVOLUCAO'                # Status
    ]

    logger.info(f"Starting ETL process for year {YEAR}")

    disease_list = get_disease_list()

    for acronym, name in disease_list.items():
        logger.info(f"Processing disease: {name} ({acronym})")
        
        try:
            raw_df = download_raw_data(acronym, YEAR)
            
            if raw_df.empty:
                logger.warning(f"No data returned for {acronym} in {YEAR}")
                continue

            raw_file_path = os.path.join(RAW_DATA_DIR, f"{acronym}_{YEAR}.csv")
            raw_df.to_csv(raw_file_path, sep=';', index=False)
            logger.debug(f"Raw data saved to {raw_file_path}")

            processed_df = filter_state_and_columns(raw_df, STATE_CODE_PB, TARGET_COLUMNS)
            
            if not processed_df.empty:
                processed_file_path = os.path.join(PROCESSED_DATA_DIR, f"{acronym}_{YEAR}_PB.csv")
                processed_df.to_csv(processed_file_path, sep=';', index=False)
                logger.info(f"Successfully processed {len(processed_df)} cases for {acronym} in PB")
            else:
                logger.info(f"National data downloaded for {acronym}, but no cases found for PB")
                
        except Exception as e:
            logger.error(f"Critical error processing {acronym}: {str(e)}")

    logger.info("ETL process finished.")

if __name__ == "__main__":
    main()