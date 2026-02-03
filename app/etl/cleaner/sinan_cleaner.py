import pandas as pd
from app.utils.logger import logger 

def clean_sinan_age(age_raw):
    try:
        age_str = str(int(float(age_raw))).zfill(4)
        if age_str.startswith('4'):
            return int(age_str[1:])
        return 0
    except:
        return 0
        

def calcular_dv_ibge(codigo_6):
    codigo = str(codigo_6)
    if len(codigo) != 6:
        return None

    pesos = [1, 2, 1, 2, 1, 2]
    soma = 0

    for i in range(6):
        mult = int(codigo[i]) * pesos[i]
        soma += mult if mult <= 9 else (mult - 9)

    resto = soma % 10
    dv = (10 - resto) % 10
    
    return f"{codigo}{dv}"


def filter_state_and_columns(df_national, state_code, mandatory_cols, optional_cols):
    if df_national.empty:
        logger.warning("Cleaner received an empty DataFrame. Skipping filtration.")
        return pd.DataFrame()

    mapping = {
        'ID_UNIT': 'ID_UNIDADE',
        'ID_MUNICIP_NOTIFICACAO': 'ID_MUNICIP',
        'DT_NOTIFICACAO': 'DT_NOTIFIC'
    }
    df_national = df_national.rename(columns={k: v for k, v in mapping.items() if k in df_national.columns})
    
    missing_mandatory = [c for c in mandatory_cols if c not in df_national.columns]
    
    if missing_mandatory:
        logger.error(f"File rejected! Missing mandatory columns: {missing_mandatory}")
        return pd.DataFrame()

    existing_optional = [c for c in optional_cols if c in df_national.columns]
    
    df_filtered = df_national[mandatory_cols + existing_optional].copy()

    for col in optional_cols:
        if col not in df_filtered.columns:
            df_filtered[col] = None
            
    logger.info(f"Filtering data for State Code: {state_code} using column: ID_MUNICIP")
    df_filtered['ID_MUNICIP'] = df_filtered['ID_MUNICIP'].astype(str)
    df_state = df_filtered[df_filtered['ID_MUNICIP'].str.startswith(str(state_code))].copy()
    
    if df_state.empty:
        logger.warning(f"Filtration complete, but no records found for state {state_code}.")
        return pd.DataFrame()
    
    logger.debug("Formatting patient age (SINAN pattern)...")
    df_state['NU_IDADE_N'] = df_state['NU_IDADE_N'].apply(clean_sinan_age)
    df_state['ID_MUNICIP'] = df_state['ID_MUNICIP'].apply(calcular_dv_ibge)
    
    logger.info(f"Successfully filtered {len(df_state)} records for the target state.")
    
    return df_state
