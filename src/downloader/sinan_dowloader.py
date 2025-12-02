from pysus.online_data.SINAN import download
from pysus.ftp.databases.sinan import SINAN
import pandas as pd
import os

def normalizar_retorno_pysus(raw_data):
    if hasattr(raw_data, 'to_dataframe'):
        return raw_data.to_dataframe()
    elif isinstance(raw_data, pd.DataFrame):
        return raw_data
    elif isinstance(raw_data, list):
        lista_dfs = []
        for item in raw_data:
            if hasattr(item, 'to_dataframe'):
                lista_dfs.append(item.to_dataframe())
            elif isinstance(item, pd.DataFrame):
                lista_dfs.append(item)
        if lista_dfs:
            return pd.concat(lista_dfs)
    return pd.DataFrame()

def obter_lista_doencas():
    try:
        print("Conectando ao metadados do SINAN...")
        sinan_metadata = SINAN().load()
        return sinan_metadata.diseases
    except Exception as e:
        print(f"Aviso: Metadados offline ({e}). Usando lista básica.")
        # TODO popular mais essa lista default
        return {
            'DENG': 'Dengue', 
            'CHIK': 'Chikungunya', 
            'ZIKA': 'Zika', 
            'ANIM': 'Animais_Peconhentos',
            'IEXO': 'Intoxicacao_Exogena',
            'LEIV': 'Leishmaniose_Visceral'
        }

def baixar_dados_brutos(sigla, ano):
    print(f" Baixando {sigla} ({ano})...")
    try:
        raw_data = download(diseases=sigla, years=ano)
        return normalizar_retorno_pysus(raw_data)
    except Exception as e:
        if "No objects to concatenate" in str(e):
            return pd.DataFrame()
        print(f" Erro no download de {sigla}: {e}")
        return pd.DataFrame()
