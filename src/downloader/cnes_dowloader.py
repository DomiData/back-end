import requests
import zipfile
import os
import shutil
from datetime import datetime
import urllib3

urllib3.disable_warnings()

def baixar_cnes_bruto(output_dir):

    BASE_URL = "https://cnes.datasus.gov.br/EstatisticasServlet"
    MAX_TENTATIVAS = 12
    agora = datetime.now()

    for i in range(MAX_TENTATIVAS):
        mes_calc = agora.month - i
        ano_calc = agora.year
        while mes_calc <= 0:
            mes_calc += 12
            ano_calc -= 1
        competencia = f"{ano_calc}{mes_calc:02d}"
        nome_zip = f"BASE_DE_DADOS_CNES_{competencia}.ZIP"
        try:            
            response = requests.get(
                BASE_URL, params={'path': nome_zip}, 
                stream=True, verify=False, timeout=60
            )

            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' in content_type:
                continue
            
            iterator = response.iter_content(chunk_size=4)
            primeiros_bytes = next(iterator, b'')

            if not primeiros_bytes.startswith(b'PK'):
                continue

            print(f"Baixando... (Isso pode demorar)")
            zip_path = os.path.join(output_dir, f"temp_cnes_{competencia}.zip")
            with open(zip_path, 'wb') as f:
                f.write(primeiros_bytes)
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            arquivo_final = None
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.startswith('tbEstabelecimento'):
                        zip_ref.extract(file, output_dir)
                        arquivo_final = os.path.join(output_dir, file)
                        break
            os.remove(zip_path)

            if arquivo_final:
                return arquivo_final

        except Exception as e:
            print(f"  Erro: {e}")
            
    print("Nenhum dado do CNES encontrado.")
    return None