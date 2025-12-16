from downloader.cnes_downloader import baixar_cnes_bruto
from cleaner.cnes_cleaner import processar_cnes
import os

def main():
    ESTADO = '25'

    colunas = [
        'CO_CNES', 
        'NO_FANTASIA', 
        'NU_LATITUDE', 
        'NU_LONGITUDE', 
        'CO_MUNICIPIO_GESTOR', 
        'TP_UNIDADE', 
        'NO_BAIRRO'
    ]

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

    RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
    PROCESSED_DIR = os.path.join(PROJECT_ROOT, "cnes")

    arquivo_bruto = baixar_cnes_bruto(RAW_DIR)
    
    df_limpo = processar_cnes(arquivo_bruto, ESTADO, colunas)
    caminho_final = os.path.join(PROCESSED_DIR, "CNES_PB_MAPA.csv")
    df_limpo.to_csv(caminho_final, sep=';', index=False)


if __name__ == "__main__":
    main()