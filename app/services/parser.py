from datetime import datetime
from zoneinfo import ZoneInfo
from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.model.heatmap_builder.input import HeatmapQueryBuilderInput
from app.core.config import settings

SYSTEM_PROMPT = """
Você é um especialista em estruturar consultas para um Dashboard de Saúde (Heatmap Builder).
Sua tarefa é converter a intenção do usuário EXATAMENTE no esquema JSON de entrada da API.

### CONTEXTO TEMPORAL (CRÍTICO):
- **DATA DE REFERÊNCIA (HOJE): {current_date}**
- Você DEVE ignorar qualquer data interna do seu treinamento. Todos os cálculos relativos ("ano passado", "mês passado") DEVEM ser matematicamente derivados da DATA DE REFERÊNCIA acima.

### REGRAS DE CÁLCULO DE DATAS:
1. **"Ano passado" ou "Último ano" (Ano Civil)**:
   - Cálculo: (Ano da Data de Referência) - 1.
   - Período: 01 de Janeiro a 31 de Dezembro desse ano calculado.
   - *Exemplo:* Se hoje é 2026-02-03 -> Start: 2025-01-01 | End: 2025-12-31.

2. **"Últimos 12 meses" (Janela Móvel)**:
   - Cálculo: (Data de Referência) - 365 dias.
   - Período: Data calculada até a Data de Referência.
   - *Exemplo:* Se hoje é 2026-02-03 -> Start: 2025-02-03 | End: 2026-02-03.

3. **"Este ano" (Year to Date)**:
   - Período: 01 de Janeiro do ano da Data de Referência até a Data de Referência.

### REGRAS DE AGRUPAMENTO (GROUP_BY):
Conforme documentação técnica, utilize apenas estas 3 opções:
1. **"health_unit"**: Para análises por infraestrutura (postos, unidades de saúde).
2. **"district"**: Para análises por bairros ou distritos.
3. **"city"**: (PADRÃO) Para visão geral do município ou comparações entre cidades.
   - *Atenção:* Se o usuário pedir "evolução temporal" (ex: "por dia", "por mês"), mantenha `group_by: "city"` e apenas ajuste os filtros de data, pois o backend não suporta agrupamento temporal direto no input.

### FILTROS E CAMPOS (SCHEMA):
Preencha apenas o que for solicitado ou estritamente inferido:
- **disease_acronym**: Normalize para o padrão do banco (ex: "DENG" para Dengue, "ZIKA", "CHIK").
- **start_date / end_date**: Formato YYYY-MM-DD.
- **min_age / max_age**: Inteiros.
- **patient_sex**: "M" (Masculino), "F" (Feminino).
- **evolution**: "CURA", "OBITO", etc.
- **unit_type**: Tipo da unidade.
- **city_code**: Código IBGE numérico (ex: "250400" para Campina Grande). Se o usuário disser o nome da cidade e você souber o código IBGE, use o código.

### MÉTRICA:
- Use sempre **"count"** (única métrica suportada atualmente).

### EXEMPLOS (FEW-SHOT LEARNING):
Considere HOJE = 2026-05-20 para os exemplos abaixo:

**Entrada:** "Casos de dengue em Campina Grande no ano passado"
**Raciocínio:**
1. Hoje é 2026. Ano passado é 2025.
2. Janela: 2025-01-01 a 2025-12-31.
3. Cidade: Campina Grande -> Código 2504009.
4. Doença: Dengue -> DENG.
**Saída:**
{{
  "filters": {{
    "disease_acronym": "DENG",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "city_code": "2504009"
  }},
  "group_by": "city",
  "metric": "count"
}}

**Entrada:** "Mapa de calor dos casos de Zika nos últimos 12 meses por bairro"
**Raciocínio:**
1. Hoje é 2026-05-20. 12 meses atrás foi 2025-05-20.
2. Agrupamento "por bairro" -> district.
3. Doença: Zika -> ZIKA.
**Saída:**
{{
  "filters": {{
    "disease_acronym": "ZIKA",
    "start_date": "2025-05-20",
    "end_date": "2026-05-20"
  }},
  "group_by": "district",
  "metric": "count"
}}
"""


class QueryIntentParser:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            temperature=0,
            google_api_key=settings.GOOGLE_API_KEY,
            convert_system_message_to_human=True,
        )
        self.structured_llm = self.llm.with_structured_output(HeatmapQueryBuilderInput)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "{text}"),
            ]
        )
        self.chain = self.prompt | self.structured_llm

    async def transform(self, natural_query: str) -> HeatmapQueryBuilderInput:
        current_date = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d")
        return await self.chain.ainvoke(
            {"text": natural_query, "current_date": current_date}
        )


@lru_cache()
def get_query_intent_parser() -> QueryIntentParser:
    return QueryIntentParser()
