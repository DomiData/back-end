import json

from langchain_core.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.query.agent_builder import AgentQueryBuilder

DISEASE_CODE_MAP = {
    # Arboviroses
    "dengue": "DENG",
    "chikungunya": "CHIK",
    "febre de chikungunya": "CHIK",
    "zika": "ZIKA",
    # Doencas bacterianas
    "leptospirose": "LEPT",
    "lepitospirose": "LEPT",
    "coqueluche": "COQU",
    "coquelute": "COQU",
    "pertussis": "COQU",
    "colera": "COLE",
    "difteria": "DIFT",
    "botulismo": "BOTU",
    "hanseniase": "HANS",
    "lepra": "HANS",
    "tuberculose": "TUBE",
    "tetano acidental": "TETA",
    "tetano neonatal": "TETN",
    "febre tifoide": "FTIF",
    "febre tifoidea": "FTIF",
    # Doencas parasitarias
    "leishmaniose visceral": "LEIV",
    "calazar": "LEIV",
    "leishmaniose tegumentar": "LTAN",
    "leishmaniose tegumentar americana": "LTAN",
    "malaria": "MALA",
    "esquistossomose": "ESQU",
    "doenca de chagas": "CHAG",
    "chagas": "CHAG",
    # Doencas virais
    "hepatites virais": "HEPA",
    "hepatite": "HEPA",
    "hantavirose": "HANT",
    "raiva humana": "RAIV",
    "raiva": "RAIV",
    "meningite": "MENI",
    "febre maculosa": "FMAC",
    "febre amarela": "FAMA",
    "influenza": "INFL",
    "influenza pandemica": "INFL",
    # Acidentes e intoxicacoes
    "animais peconhentos": "ANIM",
    "acidente por animais peconhentos": "ANIM",
    "intoxicacao exogena": "IEXO",
    # Doencas exantematicas
    "doencas exantematicas": "EXAN",
    "exantematicas": "EXAN",
    "sarampo": "EXAN",
    "rubeola": "EXAN",
}


def _resolve_disease_code(disease_name: str) -> str:
    name_lower = disease_name.lower().strip()
    if name_lower in DISEASE_CODE_MAP:
        return DISEASE_CODE_MAP[name_lower]
    return name_lower.upper()


def create_agent_tools(session: AsyncSession) -> list:
    builder = AgentQueryBuilder(session)

    @tool
    async def consultar_info_doenca(doenca: str) -> str:
        """Retorna informacoes educativas gerais sobre uma doenca (causas, sintomas,
        fatores de risco, complicacoes, prevencao, quando procurar atendimento).
        Use esta ferramenta quando o usuario perguntar sobre informacoes gerais de uma doenca.

        Args:
            doenca: Nome da doenca em portugues (ex: dengue, chikungunya, zika,
                leptospirose, coqueluche, leishmaniose visceral, meningite,
                hanseniase, hepatites virais, tuberculose, malaria)
        """
        diseases = await builder.list_diseases()
        code = _resolve_disease_code(doenca)
        has_data = any(d["acronym"] == code for d in diseases)

        result = {
            "doenca": doenca,
            "instrucao": (
                f"Forneca informacoes educativas gerais sobre {doenca}: "
                "causas, sintomas, fatores de risco, complicacoes, prevencao "
                "e quando procurar atendimento medico. "
                "Lembre-se: apenas informacoes educativas, nunca prescreva medicamentos."
            ),
            "dados_projeto_disponiveis": has_data,
            "tipo_fonte": "general_knowledge",
        }
        return json.dumps(result, ensure_ascii=False)

    @tool
    async def consultar_tendencia(doenca: str) -> str:
        """Retorna dados historicos de tendencia de uma doenca a partir do banco
        de dados do projeto Domidata (serie temporal de casos notificados).
        Use esta ferramenta quando o usuario perguntar sobre tendencias, historico
        de casos, ou evolucao de uma doenca ao longo do tempo.

        Args:
            doenca: Nome da doenca (ex: dengue, chikungunya, zika, leptospirose,
                coqueluche, leishmaniose visceral, meningite, hanseniase)
        """
        code = _resolve_disease_code(doenca)
        result = await builder.get_trend(code)
        if result.get("available"):
            result["tipo_fonte"] = "database"
            result["detalhe_fonte"] = f"banco de dados - tendencia {doenca}"
        return json.dumps(result, ensure_ascii=False)

    @tool
    async def consultar_sazonalidade(doenca: str) -> str:
        """Retorna analise de sazonalidade de uma doenca: meses de pico, meses de
        baixa, padroes sazonais baseados nos dados historicos do projeto Domidata.
        Use esta ferramenta quando o usuario perguntar sobre periodos do ano,
        sazonalidade, epocas de maior ou menor incidencia.

        Args:
            doenca: Nome da doenca (ex: dengue, chikungunya, zika, leptospirose,
                coqueluche, leishmaniose visceral, meningite, hanseniase)
        """
        code = _resolve_disease_code(doenca)
        result = await builder.get_seasonality(code)
        if result.get("available"):
            result["tipo_fonte"] = "database"
            result["detalhe_fonte"] = f"banco de dados - sazonalidade {doenca}"
        return json.dumps(result, ensure_ascii=False)

    @tool
    async def consultar_demograficos(doenca: str) -> str:
        """Retorna dados demograficos sobre os casos de uma doenca: distribuicao
        por sexo, estatisticas de idade, distribuicao por evolucao do caso.
        Use esta ferramenta quando o usuario perguntar sobre perfil dos pacientes,
        faixa etaria, sexo, ou desfecho dos casos.

        Args:
            doenca: Nome da doenca (ex: dengue, chikungunya, zika, leptospirose,
                coqueluche, leishmaniose visceral, meningite, hanseniase)
        """
        code = _resolve_disease_code(doenca)
        result = await builder.get_demographics(code)
        if result.get("available"):
            result["tipo_fonte"] = "database"
            result["detalhe_fonte"] = f"banco de dados - demograficos {doenca}"
        return json.dumps(result, ensure_ascii=False)

    @tool
    async def consultar_distribuicao_geografica(doenca: str) -> str:
        """Retorna a distribuicao geografica dos casos de uma doenca: casos por
        bairro/distrito, unidades de saude com mais notificacoes.
        Use esta ferramenta quando o usuario perguntar sobre localizacao dos casos,
        bairros mais afetados, ou unidades de saude.

        Args:
            doenca: Nome da doenca (ex: dengue, chikungunya, zika, leptospirose,
                coqueluche, leishmaniose visceral, meningite, hanseniase)
        """
        code = _resolve_disease_code(doenca)
        result = await builder.get_geographic_distribution(code)
        if result.get("available"):
            result["tipo_fonte"] = "database"
            result["detalhe_fonte"] = (
                f"banco de dados - distribuicao geografica {doenca}"
            )
        return json.dumps(result, ensure_ascii=False)

    @tool
    async def consultar_distribuicao_por_municipio(doenca: str) -> str:
        """Retorna a distribuicao dos casos de uma doenca agrupados por municipio
        (cidade) do estado da Paraiba. Use esta ferramenta quando o usuario
        perguntar sobre municipios, cidades mais afetadas, ou comparacao entre
        municipios.

        Args:
            doenca: Nome da doenca (ex: dengue, chikungunya, zika, leptospirose,
                coqueluche, leishmaniose visceral, meningite, hanseniase)
        """
        code = _resolve_disease_code(doenca)
        result = await builder.get_distribution_by_municipality(code)
        if result.get("available"):
            result["tipo_fonte"] = "database"
            result["detalhe_fonte"] = (
                f"banco de dados - distribuicao por municipio {doenca}"
            )
        return json.dumps(result, ensure_ascii=False)

    return [
        consultar_info_doenca,
        consultar_tendencia,
        consultar_sazonalidade,
        consultar_demograficos,
        consultar_distribuicao_geografica,
        consultar_distribuicao_por_municipio,
    ]
