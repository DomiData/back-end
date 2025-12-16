import pandas as pd

def processar_cnes(caminho_csv_bruto, estado_filtro, colunas_desejadas):
    print("Iniciando processamento do CNES...")
    
    try:
        df = pd.read_csv(caminho_csv_bruto, sep=';', encoding='ISO-8859-1', 
                         usecols=lambda c: c in colunas_desejadas,
        dtype={'CO_CNES': str, 'CO_MUNICIPIO_GESTOR': str})
        df_pb = df[df['CO_MUNICIPIO_GESTOR'].str.startswith(estado_filtro)].copy()
        df_final = df_pb.dropna(subset=['NU_LATITUDE', 'NU_LONGITUDE'])
        
        return df_final

    except Exception as e:
        print(f"Erro ao processar CNES: {e}")
        return pd.DataFrame()