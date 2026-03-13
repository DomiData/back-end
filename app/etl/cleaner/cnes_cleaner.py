import pandas as pd
from app.utils.logger import logger


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


def process_cnes_data(raw_csv_path, state_filter, target_columns):
    logger.info(f"Starting CNES data processing for file: {raw_csv_path}")

    try:
        df = pd.read_csv(
            raw_csv_path,
            sep=";",
            encoding="ISO-8859-1",
            usecols=lambda c: c in target_columns,
            dtype={"CO_CNES": str, "CO_MUNICIPIO_GESTOR": str},
        )

        if df.empty:
            logger.warning("The raw CNES file is empty.")
            return pd.DataFrame()

        logger.debug(f"Filtering units for state code: {state_filter}")
        df_state = df[
            df["CO_MUNICIPIO_GESTOR"].str.startswith(str(state_filter))
        ].copy()

        logger.info(f"Found {len(df_state)} health units in the target state.")

        df_state["NU_LATITUDE"] = (
            df_state["NU_LATITUDE"].astype(str).str.replace(",", ".")
        )
        df_state["NU_LONGITUDE"] = (
            df_state["NU_LONGITUDE"].astype(str).str.replace(",", ".")
        )

        df_state["NU_LATITUDE"] = pd.to_numeric(
            df_state["NU_LATITUDE"], errors="coerce"
        )
        df_state["NU_LONGITUDE"] = pd.to_numeric(
            df_state["NU_LONGITUDE"], errors="coerce"
        )

        df_state["CO_MUNICIPIO_GESTOR"] = df_state["CO_MUNICIPIO_GESTOR"].apply(
            calcular_dv_ibge
        )

        df_final = df_state.dropna(
            subset=["NU_LATITUDE", "NU_LONGITUDE", "CO_MUNICIPIO_GESTOR"]
        )
        logger.info(
            f"Processing complete. {len(df_final)} valid units ready for the map."
        )

        return df_final

    except Exception as e:
        logger.error(f"Failed to process CNES data: {e}")
        return pd.DataFrame()
