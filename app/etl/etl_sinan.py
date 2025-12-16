from downloader.sinan_downloader import baixar_dados_brutos, obter_lista_doencas
from cleaner.sinan_cleaner import filtrar_estado_e_colunas
import os

def main():
    ANO = 2025
    ESTADO_FILTRO = '25'

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))    
    PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
    RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
    PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
    
    COLUNAS_DESEJADAS = [
    'DT_NOTIFIC', 'DT_SIN_PRI', 'DT_OCORR', # Datas possíveis
    'ID_MUNICIP', 'ID_MUNICIP_NOTIFICACAO', # Local da Notificação
    'ID_UNIDADE', 'ID_UNIT',                # O Posto de Saúde (Crucial)
    'ID_MN_RESI',                           # Onde Mora
    'NU_IDADE_N', 'CS_SEXO',                # Perfil
    'CLASSI_FIN', 'EVOLUCAO'                # Status
    ]

    lista_doencas = obter_lista_doencas()
    for sigla, nome in lista_doencas.items():
        data = baixar_dados_brutos(sigla, ANO)
        
        if data.empty:
            print("  [Vazio] Nenhum dado retornado.")
            continue

        arquivo = os.path.join(RAW_DATA_DIR, f"{sigla}_{ANO}.csv")
        data.to_csv(arquivo, sep=';', index=False)

        df_pb = filtrar_estado_e_colunas(data, ESTADO_FILTRO, COLUNAS_DESEJADAS)
        if not df_pb.empty:
            arquivo = os.path.join(PROCESSED_DATA_DIR, f"{sigla}_{ANO}_PB.csv")
            df_pb.to_csv(arquivo, sep=';', index=False)
        else:
            print("  [Info] Dados nacionais baixados, mas sem casos na PB.")

if __name__ == "__main__":
    main()