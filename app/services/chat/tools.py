import json

from langchain_core.tools import tool

from app.services.chat import data_loader


_data_dir: str = ""


def set_data_dir(data_dir: str) -> None:
    global _data_dir
    _data_dir = data_dir


@tool
def consultar_info_doenca(doenca: str) -> str:
    """Retorna informacoes educativas gerais sobre uma doenca (causas, sintomas,
    fatores de risco, complicacoes, prevencao, quando procurar atendimento).
    Use esta ferramenta quando o usuario perguntar sobre informacoes gerais de uma doenca.

    Args:
        doenca: Nome da doenca em portugues (ex: dengue, chikungunya, zika)
    """
    # Check if we have project data for this disease
    available = data_loader.list_available_diseases(_data_dir)
    has_project_data = any(
        d["name"].lower() == doenca.lower() or d["code"].lower() == doenca.lower()
        for d in available
    )

    result = {
        "doenca": doenca,
        "instrucao": (
            f"Forneca informacoes educativas gerais sobre {doenca}: "
            "causas, sintomas, fatores de risco, complicacoes, prevencao "
            "e quando procurar atendimento medico. "
            "Lembre-se: apenas informacoes educativas, nunca prescreva medicamentos."
        ),
        "dados_projeto_disponiveis": has_project_data,
        "tipo_fonte": "general_knowledge",
    }
    return json.dumps(result, ensure_ascii=False)


@tool
def consultar_tendencia(doenca: str) -> str:
    """Retorna dados historicos de tendencia de uma doenca a partir dos dados
    do projeto Domidata (serie temporal de casos notificados).
    Use esta ferramenta quando o usuario perguntar sobre tendencias, historico
    de casos, ou evolucao de uma doenca ao longo do tempo.

    Args:
        doenca: Nome da doenca (ex: dengue, chikungunya, zika)
    """
    result = data_loader.load_time_series(doenca, _data_dir)
    if result.get("available"):
        result["tipo_fonte"] = "prediction_data"
        result["detalhe_fonte"] = f"time_series.csv - {doenca}"
    return json.dumps(result, ensure_ascii=False)


@tool
def consultar_previsao(doenca: str) -> str:
    """Retorna dados de previsao/forecast de casos futuros de uma doenca
    gerados pelo pipeline de predicao do projeto Domidata.
    Use esta ferramenta quando o usuario perguntar sobre previsoes,
    projecoes futuras ou estimativas de casos.

    Args:
        doenca: Nome da doenca (ex: dengue, chikungunya, zika)
    """
    result = data_loader.load_forecast(doenca, _data_dir)
    if result.get("available"):
        result["tipo_fonte"] = "prediction_data"
        result["detalhe_fonte"] = f"forecast.csv - {doenca}"
    return json.dumps(result, ensure_ascii=False)


@tool
def consultar_sazonalidade(doenca: str) -> str:
    """Retorna analise de sazonalidade de uma doenca: meses de pico, meses de
    baixa, padroes sazonais baseados nos dados historicos do projeto Domidata.
    Use esta ferramenta quando o usuario perguntar sobre periodos do ano,
    sazonalidade, epocas de maior ou menor incidencia.

    Args:
        doenca: Nome da doenca (ex: dengue, chikungunya, zika)
    """
    result = data_loader.get_seasonality_summary(doenca, _data_dir)
    if result.get("available"):
        result["tipo_fonte"] = "prediction_data"
        result["detalhe_fonte"] = f"time_series.csv (sazonalidade) - {doenca}"
    return json.dumps(result, ensure_ascii=False)


ALL_TOOLS = [
    consultar_info_doenca,
    consultar_tendencia,
    consultar_previsao,
    consultar_sazonalidade,
]
