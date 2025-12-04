"""
Utility functions for merging SINAN CSV files.

This module provides functions to merge CSV files from data/processed directory,
adding a disease column based on the filename prefix (before first underscore).
"""

import os
from typing import Optional

import pandas as pd


def extrair_codigo_doenca(nome_arquivo: str) -> str:
    return nome_arquivo.split("_")[0]


def mesclar_csvs_sinan(
    diretorio_processados: str, caminho_saida: Optional[str] = "data/processed/merged"
) -> pd.DataFrame:
    if not os.path.exists(diretorio_processados):
        raise FileNotFoundError(f"Directory not found: {diretorio_processados}")

    arquivos_csv = [f for f in os.listdir(diretorio_processados) if f.endswith(".csv")]

    if not arquivos_csv:
        raise ValueError(f"No CSV files found in {diretorio_processados}")

    dataframes = []

    for arquivo in arquivos_csv:
        try:
            codigo_doenca = extrair_codigo_doenca(arquivo)
            caminho_completo = os.path.join(diretorio_processados, arquivo)
            df = pd.read_csv(caminho_completo, sep=";")
            df["DOEN"] = codigo_doenca
            dataframes.append(df)

        except Exception:
            continue

    if not dataframes:
        raise ValueError("No valid CSV files could be loaded")

    merged_df = pd.concat(dataframes, ignore_index=True)

    if caminho_saida:
        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        merged_df.to_csv(caminho_saida, sep=";", index=False)

    return merged_df
