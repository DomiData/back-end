import pandas as pd
from app.utils.logger import logger

def process_cnes_data(raw_csv_path, state_filter, target_columns):
    logger.info(f"Starting CNES data processing for file: {raw_csv_path}")
    
    try:
        df = pd.read_csv(
            raw_csv_path, 
            sep=';', 
            encoding='ISO-8859-1', 
            usecols=lambda c: c in target_columns,
            dtype={'CO_CNES': str, 'CO_MUNICIPIO_GESTOR': str}
        )
        
        if df.empty:
            logger.warning("The raw CNES file is empty.")
            return pd.DataFrame()

        logger.debug(f"Filtering units for state code: {state_filter}")
        df_state = df[df['CO_MUNICIPIO_GESTOR'].str.startswith(str(state_filter))].copy()
        
        logger.info(f"Found {len(df_state)} health units in the target state.")
        df_final = df_state.dropna(subset=['NU_LATITUDE', 'NU_LONGITUDE'])
        logger.info(f"Processing complete. {len(df_final)} valid units ready for the map.")
        
        return df_final

    except Exception as e:
        logger.error(f"Failed to process CNES data: {e}")
        return pd.DataFrame()