import requests
import zipfile
import os
import shutil
from datetime import datetime
import urllib3
from app.utils.logger import logger

urllib3.disable_warnings()

def download_raw_cnes(output_dir):
    BASE_URL = "https://cnes.datasus.gov.br/EstatisticasServlet"
    MAX_ATTEMPTS = 12
    now = datetime.now()

    logger.info(f"Starting search for the most recent CNES database (Max attempts: {MAX_ATTEMPTS})")

    for i in range(MAX_ATTEMPTS):
        calc_month = now.month - i
        calc_year = now.year
        
        while calc_month <= 0:
            calc_month += 12
            calc_year -= 1
            
        competence = f"{calc_year}{calc_month:02d}"
        zip_name = f"BASE_DE_DADOS_CNES_{competence}.ZIP"
        
        logger.debug(f"Trying competence: {competence}...")

        try:            
            response = requests.get(
                BASE_URL, 
                params={'path': zip_name}, 
                stream=True, 
                verify=False, 
                timeout=60
            )

            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' in content_type:
                continue
            
            iterator = response.iter_content(chunk_size=4)
            first_bytes = next(iterator, b'')

            if not first_bytes.startswith(b'PK'):
                logger.debug(f"Competence {competence} not available on server.")
                continue

            logger.info(f"Database found for {competence}! Starting download...")
            
            zip_path = os.path.join(output_dir, f"temp_cnes_{competence}.zip")
            
            with open(zip_path, 'wb') as f:
                f.write(first_bytes)
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            final_file = None
            logger.info("Extracting establishment table (tbEstabelecimento)...")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.startswith('tbEstabelecimento'):
                        zip_ref.extract(file, output_dir)
                        final_file = os.path.join(output_dir, file)
                        logger.info(f"File extracted successfully: {file}")
                        break
            os.remove(zip_path)

            if final_file:
                return final_file

        except Exception as e:
            logger.error(f"Error while attempting to download competence {competence}: {e}")
            
    logger.critical("No CNES data found after checking the last 12 months.")
    return None