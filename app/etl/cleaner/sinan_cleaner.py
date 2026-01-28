import pandas as pd
from app.utils.logger import logger 

def filter_state_and_columns(df_national, state_code, target_columns):
    if df_national.empty:
        logger.warning("Cleaner received an empty DataFrame. Skipping filtration.")
        return pd.DataFrame()

    existing_cols = [c for c in target_columns if c in df_national.columns]
    
    if not existing_cols:
        logger.error("None of the target columns were found in the DataFrame.")
        return pd.DataFrame()
    
    df_filtered = df_national[existing_cols].copy()
    logger.debug(f"Columns filtered. {len(existing_cols)} of {len(target_columns)} columns matched.")
    municipality_col = next((c for c in df_filtered.columns if 'MUNICIP' in c), None)
    
    if municipality_col:
        logger.info(f"Filtering data for State Code: {state_code} using column: {municipality_col}")
        df_filtered[municipality_col] = df_filtered[municipality_col].astype(str)
        df_state = df_filtered[df_filtered[municipality_col].str.startswith(str(state_code))].copy()
        
        if df_state.empty:
            logger.warning(f"Filtration complete, but no records found for state {state_code}.")
        else:
            logger.info(f"Successfully filtered {len(df_state)} records for the target state.")
            
        return df_state
    
    logger.error("Municipality identification column not found. Could not filter by state.")
    return pd.DataFrame()