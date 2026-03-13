import json
from typing import Optional

from langchain_core.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.query.agent_builder import AgentQueryBuilder
from app.schema.builder.filters import Filters

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


def _build_filters(
    doenca: str,
    sexo: Optional[str] = None,
    idade_min: Optional[int] = None,
    idade_max: Optional[int] = None,
    evolucao: Optional[str] = None,
    codigo_municipio: Optional[str] = None,
    tipo_unidade: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
) -> Filters:
    """Build a Filters object from tool parameters."""
    from datetime import date

    kwargs: dict = {"disease_acronym": _resolve_disease_code(doenca)}

    if sexo:
        kwargs["patient_sex"] = sexo.upper()
    if idade_min is not None:
        kwargs["min_age"] = idade_min
    if idade_max is not None:
        kwargs["max_age"] = idade_max
    if evolucao:
        kwargs["evolution"] = evolucao
    if codigo_municipio:
        kwargs["city_code"] = codigo_municipio
    if tipo_unidade:
        kwargs["unit_type"] = tipo_unidade
    if data_inicio:
        kwargs["start_date"] = date.fromisoformat(data_inicio)
    if data_fim:
        kwargs["end_date"] = date.fromisoformat(data_fim)

    return Filters(**kwargs)


def _describe_filters(
    sexo: Optional[str] = None,
    idade_min: Optional[int] = None,
    idade_max: Optional[int] = None,
    evolucao: Optional[str] = None,
    codigo_municipio: Optional[str] = None,
    tipo_unidade: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
) -> str:
    """Return a human-readable description of active filters."""
    parts = []
    if sexo:
        parts.append(f"sexo={sexo.upper()}")
    if idade_min is not None:
        parts.append(f"idade>={idade_min}")
    if idade_max is not None:
        parts.append(f"idade<={idade_max}")
    if evolucao:
        parts.append(f"evolucao={evolucao}")
    if codigo_municipio:
        parts.append(f"municipio={codigo_municipio}")
    if tipo_unidade:
        parts.append(f"tipo_unidade={tipo_unidade}")
    if data_inicio:
        parts.append(f"de={data_inicio}")
    if data_fim:
        parts.append(f"ate={data_fim}")
    return ", ".join(parts) if parts else "sem filtros adicionais"


def create_agent_tools(session: AsyncSession) -> list:
    builder = AgentQueryBuilder(session)

    @tool
    async def listar_doencas() -> str:
        """Lista todas as doencas disponiveis no banco de dados do projeto Domidata.
        Use esta ferramenta para descobrir quais doencas possuem dados antes de
        informar ao usuario que nao ha dados disponiveis.
        """
        diseases = await builder.list_diseases()
        return json.dumps(
            {"doencas": diseases, "total": len(diseases)},
            ensure_ascii=False,
        )

    @tool
    async def consultar_info_doenca(doenca: str) -> str:
        """Retorna informacoes educativas gerais sobre uma doenca (causas, sintomas,
        fatores de risco, complicacoes, prevencao, quando procurar atendimento).
        Use esta ferramenta quando o usuario perguntar sobre informacoes gerais de uma doenca.

        Args:
            doenca: Nome da doenca em portugues (ex: dengue, tuberculose, meningite)
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
    async def consultar_tendencia(
        doenca: str,
        sexo: Optional[str] = None,
        idade_min: Optional[int] = None,
        idade_max: Optional[int] = None,
        evolucao: Optional[str] = None,
        codigo_municipio: Optional[str] = None,
        tipo_unidade: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> str:
        """Retorna dados historicos de tendencia de uma doenca a partir do banco
        de dados do projeto Domidata (serie temporal de casos notificados).
        Use esta ferramenta quando o usuario perguntar sobre tendencias, historico
        de casos, ou evolucao ao longo do tempo.

        Todos os filtros sao opcionais e podem ser combinados para analises
        cruzadas (ex: tendencia de dengue em mulheres idosas).

        Args:
            doenca: Nome da doenca (ex: dengue, tuberculose, meningite)
            sexo: Filtrar por sexo - M (masculino) ou F (feminino)
            idade_min: Filtrar por idade minima do paciente
            idade_max: Filtrar por idade maxima do paciente
            evolucao: Filtrar por evolucao/desfecho do caso (ex: CURA, OBITO)
            codigo_municipio: Filtrar por codigo IBGE do municipio
            tipo_unidade: Filtrar por tipo de unidade de saude
            data_inicio: Data inicial no formato YYYY-MM-DD
            data_fim: Data final no formato YYYY-MM-DD
        """
        filters = _build_filters(
            doenca,
            sexo,
            idade_min,
            idade_max,
            evolucao,
            codigo_municipio,
            tipo_unidade,
            data_inicio,
            data_fim,
        )
        result = await builder.get_trend(filters)
        if result.get("available"):
            filter_desc = _describe_filters(
                sexo,
                idade_min,
                idade_max,
                evolucao,
                codigo_municipio,
                tipo_unidade,
                data_inicio,
                data_fim,
            )
            result["tipo_fonte"] = "database"
            result["detalhe_fonte"] = f"banco de dados - tendencia {doenca}"
            result["filtros_aplicados"] = filter_desc
        return json.dumps(result, ensure_ascii=False)

    @tool
    async def consultar_sazonalidade(
        doenca: str,
        sexo: Optional[str] = None,
        idade_min: Optional[int] = None,
        idade_max: Optional[int] = None,
        evolucao: Optional[str] = None,
        codigo_municipio: Optional[str] = None,
        tipo_unidade: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> str:
        """Retorna analise de sazonalidade de uma doenca: meses de pico, meses de
        baixa, padroes sazonais baseados nos dados historicos do projeto Domidata.
        Use esta ferramenta quando o usuario perguntar sobre periodos do ano,
        sazonalidade, epocas de maior ou menor incidencia.

        Todos os filtros sao opcionais e podem ser combinados.

        Args:
            doenca: Nome da doenca (ex: dengue, tuberculose, meningite)
            sexo: Filtrar por sexo - M (masculino) ou F (feminino)
            idade_min: Filtrar por idade minima do paciente
            idade_max: Filtrar por idade maxima do paciente
            evolucao: Filtrar por evolucao/desfecho do caso (ex: CURA, OBITO)
            codigo_municipio: Filtrar por codigo IBGE do municipio
            tipo_unidade: Filtrar por tipo de unidade de saude
            data_inicio: Data inicial no formato YYYY-MM-DD
            data_fim: Data final no formato YYYY-MM-DD
        """
        filters = _build_filters(
            doenca,
            sexo,
            idade_min,
            idade_max,
            evolucao,
            codigo_municipio,
            tipo_unidade,
            data_inicio,
            data_fim,
        )
        result = await builder.get_seasonality(filters)
        if result.get("available"):
            filter_desc = _describe_filters(
                sexo,
                idade_min,
                idade_max,
                evolucao,
                codigo_municipio,
                tipo_unidade,
                data_inicio,
                data_fim,
            )
            result["tipo_fonte"] = "database"
            result["detalhe_fonte"] = f"banco de dados - sazonalidade {doenca}"
            result["filtros_aplicados"] = filter_desc
        return json.dumps(result, ensure_ascii=False)

    @tool
    async def consultar_demograficos(
        doenca: str,
        sexo: Optional[str] = None,
        idade_min: Optional[int] = None,
        idade_max: Optional[int] = None,
        evolucao: Optional[str] = None,
        codigo_municipio: Optional[str] = None,
        tipo_unidade: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> str:
        """Retorna dados demograficos sobre os casos de uma doenca: distribuicao
        por sexo, estatisticas de idade, distribuicao por evolucao do caso.
        Use esta ferramenta quando o usuario perguntar sobre perfil dos pacientes,
        faixa etaria, sexo, ou desfecho dos casos.

        Todos os filtros sao opcionais e podem ser combinados.

        Args:
            doenca: Nome da doenca (ex: dengue, tuberculose, meningite)
            sexo: Filtrar por sexo - M (masculino) ou F (feminino)
            idade_min: Filtrar por idade minima do paciente
            idade_max: Filtrar por idade maxima do paciente
            evolucao: Filtrar por evolucao/desfecho do caso (ex: CURA, OBITO)
            codigo_municipio: Filtrar por codigo IBGE do municipio
            tipo_unidade: Filtrar por tipo de unidade de saude
            data_inicio: Data inicial no formato YYYY-MM-DD
            data_fim: Data final no formato YYYY-MM-DD
        """
        filters = _build_filters(
            doenca,
            sexo,
            idade_min,
            idade_max,
            evolucao,
            codigo_municipio,
            tipo_unidade,
            data_inicio,
            data_fim,
        )
        result = await builder.get_demographics(filters)
        if result.get("available"):
            filter_desc = _describe_filters(
                sexo,
                idade_min,
                idade_max,
                evolucao,
                codigo_municipio,
                tipo_unidade,
                data_inicio,
                data_fim,
            )
            result["tipo_fonte"] = "database"
            result["detalhe_fonte"] = f"banco de dados - demograficos {doenca}"
            result["filtros_aplicados"] = filter_desc
        return json.dumps(result, ensure_ascii=False)

    @tool
    async def consultar_distribuicao_geografica(
        doenca: str,
        sexo: Optional[str] = None,
        idade_min: Optional[int] = None,
        idade_max: Optional[int] = None,
        evolucao: Optional[str] = None,
        codigo_municipio: Optional[str] = None,
        tipo_unidade: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> str:
        """Retorna a distribuicao geografica dos casos de uma doenca: casos por
        bairro/distrito, unidades de saude com mais notificacoes.
        Use esta ferramenta quando o usuario perguntar sobre localizacao dos casos,
        bairros mais afetados, ou unidades de saude.

        Todos os filtros sao opcionais e podem ser combinados.

        Args:
            doenca: Nome da doenca (ex: dengue, tuberculose, meningite)
            sexo: Filtrar por sexo - M (masculino) ou F (feminino)
            idade_min: Filtrar por idade minima do paciente
            idade_max: Filtrar por idade maxima do paciente
            evolucao: Filtrar por evolucao/desfecho do caso (ex: CURA, OBITO)
            codigo_municipio: Filtrar por codigo IBGE do municipio
            tipo_unidade: Filtrar por tipo de unidade de saude
            data_inicio: Data inicial no formato YYYY-MM-DD
            data_fim: Data final no formato YYYY-MM-DD
        """
        filters = _build_filters(
            doenca,
            sexo,
            idade_min,
            idade_max,
            evolucao,
            codigo_municipio,
            tipo_unidade,
            data_inicio,
            data_fim,
        )
        result = await builder.get_geographic_distribution(filters)
        if result.get("available"):
            filter_desc = _describe_filters(
                sexo,
                idade_min,
                idade_max,
                evolucao,
                codigo_municipio,
                tipo_unidade,
                data_inicio,
                data_fim,
            )
            result["tipo_fonte"] = "database"
            result["detalhe_fonte"] = (
                f"banco de dados - distribuicao geografica {doenca}"
            )
            result["filtros_aplicados"] = filter_desc
        return json.dumps(result, ensure_ascii=False)

    @tool
    async def consultar_distribuicao_por_municipio(
        doenca: str,
        sexo: Optional[str] = None,
        idade_min: Optional[int] = None,
        idade_max: Optional[int] = None,
        evolucao: Optional[str] = None,
        tipo_unidade: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> str:
        """Retorna a distribuicao dos casos de uma doenca agrupados por municipio
        (cidade) do estado da Paraiba. Use esta ferramenta quando o usuario
        perguntar sobre municipios, cidades mais afetadas, ou comparacao entre
        municipios.

        Todos os filtros sao opcionais e podem ser combinados.
        Nota: esta ferramenta nao aceita filtro de codigo_municipio pois
        ja agrupa por municipio.

        Args:
            doenca: Nome da doenca (ex: dengue, tuberculose, meningite)
            sexo: Filtrar por sexo - M (masculino) ou F (feminino)
            idade_min: Filtrar por idade minima do paciente
            idade_max: Filtrar por idade maxima do paciente
            evolucao: Filtrar por evolucao/desfecho do caso (ex: CURA, OBITO)
            tipo_unidade: Filtrar por tipo de unidade de saude
            data_inicio: Data inicial no formato YYYY-MM-DD
            data_fim: Data final no formato YYYY-MM-DD
        """
        filters = _build_filters(
            doenca,
            sexo,
            idade_min,
            idade_max,
            evolucao,
            None,
            tipo_unidade,
            data_inicio,
            data_fim,
        )
        result = await builder.get_distribution_by_municipality(filters)
        if result.get("available"):
            filter_desc = _describe_filters(
                sexo,
                idade_min,
                idade_max,
                evolucao,
                None,
                tipo_unidade,
                data_inicio,
                data_fim,
            )
            result["tipo_fonte"] = "database"
            result["detalhe_fonte"] = (
                f"banco de dados - distribuicao por municipio {doenca}"
            )
            result["filtros_aplicados"] = filter_desc
        return json.dumps(result, ensure_ascii=False)

    return [
        listar_doencas,
        consultar_info_doenca,
        consultar_tendencia,
        consultar_sazonalidade,
        consultar_demograficos,
        consultar_distribuicao_geografica,
        consultar_distribuicao_por_municipio,
    ]
