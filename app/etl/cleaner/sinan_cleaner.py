import pandas as pd

def filtrar_estado_e_colunas(df_brasil, estado_codigo, colunas_desejadas):
    cols_existentes = [c for c in colunas_desejadas if c in df_brasil.columns]
    df_limpo = df_brasil[cols_existentes].copy()

    col_mun = next((c for c in df_limpo.columns if 'MUNICIP' in c), None)
    
    if col_mun:
        return df_limpo[df_limpo[col_mun].astype(str).str.startswith(estado_codigo)]
    
    return pd.DataFrame() # Se não tiver coluna de município, retorna vazio por segurança