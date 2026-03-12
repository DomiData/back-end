from typing import Any

from sqlalchemy import func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.disease import Disease
from app.model.health_unit import HealthUnit
from app.model.occurrence import Occurrence
from app.repository.query.builder import QueryBuilder
from app.schema.builder.filters import Filters


MONTH_NAMES_PT = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Marco",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


class AgentQueryBuilder:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_diseases(self) -> list[dict[str, Any]]:
        qb = QueryBuilder(self.session)
        qb.select(Disease.acronym, Disease.name)
        qb.stmt = qb.stmt.select_from(Disease)
        rows = await qb.execute()
        return [{"acronym": r.acronym, "name": r.name} for r in rows]

    async def get_trend(self, disease_acronym: str) -> dict[str, Any]:
        f = Filters(disease_acronym=disease_acronym)
        qb = QueryBuilder(self.session)

        year_col = extract("year", Occurrence.notification_date).label("year")
        month_col = extract("month", Occurrence.notification_date).label("month")
        count_col = func.count(Occurrence.id).label("cases")

        qb.select(year_col, month_col, count_col)
        qb.apply_filters(f)
        qb.group_by(year_col, month_col)
        qb.stmt = qb.stmt.order_by(year_col, month_col)

        rows = await qb.execute()

        if not rows:
            return {
                "available": False,
                "message": f"Nenhum dado encontrado para '{disease_acronym}'.",
            }

        monthly_data: list[dict[str, Any]] = [
            {
                "year": int(r.year),
                "month": int(r.month),
                "period": f"{int(r.year)}-{int(r.month):02d}",
                "cases": int(r.cases),
            }
            for r in rows
        ]

        cases = [int(d["cases"]) for d in monthly_data]
        total = sum(cases)
        mean = round(total / len(cases), 1)
        max_cases = max(cases)
        min_cases = min(cases)
        max_entry = next(d for d in monthly_data if d["cases"] == max_cases)

        return {
            "available": True,
            "disease_code": disease_acronym.upper(),
            "total_periods": len(monthly_data),
            "date_range": f"{monthly_data[0]['period']} a {monthly_data[-1]['period']}",
            "total_cases": total,
            "mean_monthly_cases": mean,
            "max_cases": max_cases,
            "max_cases_date": max_entry["period"],
            "min_cases": min_cases,
            "recent_periods": monthly_data[-6:],
        }

    async def get_seasonality(self, disease_acronym: str) -> dict[str, Any]:
        f = Filters(disease_acronym=disease_acronym)
        qb = QueryBuilder(self.session)

        month_col = extract("month", Occurrence.notification_date).label("month")
        count_col = func.count(Occurrence.id).label("cases")
        years_col = func.count(
            func.distinct(extract("year", Occurrence.notification_date))
        ).label("num_years")

        qb.select(month_col, count_col, years_col)
        qb.apply_filters(f)
        qb.group_by(month_col)
        qb.stmt = qb.stmt.order_by(month_col)

        rows = await qb.execute()

        if not rows:
            return {
                "available": False,
                "message": f"Nenhum dado de sazonalidade encontrado para '{disease_acronym}'.",
            }

        monthly_data: list[dict[str, Any]] = []
        for r in rows:
            m = int(r.month)
            avg = round(int(r.cases) / int(r.num_years), 1)
            monthly_data.append(
                {"month": m, "month_name": MONTH_NAMES_PT[m], "avg_cases": avg}
            )

        avgs = [d["avg_cases"] for d in monthly_data]
        overall_avg = sum(avgs) / len(avgs)

        peak = max(monthly_data, key=lambda d: d["avg_cases"])
        low = min(monthly_data, key=lambda d: d["avg_cases"])

        high_season = [
            d["month_name"] for d in monthly_data if d["avg_cases"] > overall_avg
        ]
        low_season = [
            d["month_name"] for d in monthly_data if d["avg_cases"] <= overall_avg
        ]

        return {
            "available": True,
            "disease_code": disease_acronym.upper(),
            "monthly_averages": monthly_data,
            "peak_month": peak["month_name"],
            "peak_month_avg_cases": peak["avg_cases"],
            "low_month": low["month_name"],
            "low_month_avg_cases": low["avg_cases"],
            "high_season": high_season,
            "low_season": low_season,
        }

    async def get_demographics(self, disease_acronym: str) -> dict[str, Any]:
        f = Filters(disease_acronym=disease_acronym)

        # Sex distribution
        qb_sex = QueryBuilder(self.session)
        qb_sex.select(
            Occurrence.patient_sex.label("sex"),
            func.count(Occurrence.id).label("count"),
        )
        qb_sex.apply_filters(f)
        qb_sex.group_by(Occurrence.patient_sex)
        sex_rows = await qb_sex.execute()

        if not sex_rows:
            return {
                "available": False,
                "message": f"Nenhum dado demografico encontrado para '{disease_acronym}'.",
            }

        sex_dist = {r.sex or "nao_informado": int(r.count) for r in sex_rows}

        # Age stats
        qb_age = QueryBuilder(self.session)
        qb_age.select(
            func.avg(Occurrence.patient_age).label("avg_age"),
            func.min(Occurrence.patient_age).label("min_age"),
            func.max(Occurrence.patient_age).label("max_age"),
            func.count(Occurrence.id).label("total"),
        )
        qb_age.apply_filters(f)
        age_row = (await qb_age.execute())[0]

        # Evolution distribution
        qb_evo = QueryBuilder(self.session)
        qb_evo.select(
            Occurrence.evolution.label("evolution"),
            func.count(Occurrence.id).label("count"),
        )
        qb_evo.apply_filters(f)
        qb_evo.group_by(Occurrence.evolution)
        evo_rows = await qb_evo.execute()

        evo_dist = {r.evolution or "nao_informado": int(r.count) for r in evo_rows}

        return {
            "available": True,
            "disease_code": disease_acronym.upper(),
            "total_cases": int(age_row.total),
            "sex_distribution": sex_dist,
            "age_stats": {
                "avg": round(float(age_row.avg_age), 1) if age_row.avg_age else None,
                "min": int(age_row.min_age) if age_row.min_age is not None else None,
                "max": int(age_row.max_age) if age_row.max_age is not None else None,
            },
            "evolution_distribution": evo_dist,
        }

    async def get_geographic_distribution(self, disease_acronym: str) -> dict[str, Any]:
        f = Filters(disease_acronym=disease_acronym)

        # Cases by district
        qb_dist = QueryBuilder(self.session)
        qb_dist.select(
            HealthUnit.district.label("district"),
            func.count(Occurrence.id).label("count"),
        )
        qb_dist.base_join("health_unit")
        qb_dist.apply_filters(f)
        qb_dist.group_by(HealthUnit.district)
        qb_dist.stmt = qb_dist.stmt.order_by(func.count(Occurrence.id).desc())
        dist_rows = await qb_dist.execute()

        if not dist_rows:
            return {
                "available": False,
                "message": f"Nenhum dado geografico encontrado para '{disease_acronym}'.",
            }

        districts = [
            {"district": r.district or "nao_informado", "cases": int(r.count)}
            for r in dist_rows
        ]

        # Top health units
        qb_units = QueryBuilder(self.session)
        qb_units.select(
            HealthUnit.name.label("unit_name"),
            HealthUnit.district.label("district"),
            func.count(Occurrence.id).label("count"),
        )
        qb_units.base_join("health_unit")
        qb_units.apply_filters(f)
        qb_units.group_by(HealthUnit.name, HealthUnit.district)
        qb_units.stmt = qb_units.stmt.order_by(func.count(Occurrence.id).desc()).limit(
            10
        )
        unit_rows = await qb_units.execute()

        top_units = [
            {
                "name": r.unit_name,
                "district": r.district or "nao_informado",
                "cases": int(r.count),
            }
            for r in unit_rows
        ]

        return {
            "available": True,
            "disease_code": disease_acronym.upper(),
            "by_district": districts,
            "top_health_units": top_units,
            "total_districts": len(districts),
        }

    async def get_distribution_by_municipality(
        self, disease_acronym: str
    ) -> dict[str, Any]:
        f = Filters(disease_acronym=disease_acronym)

        qb = QueryBuilder(self.session)
        qb.select(
            HealthUnit.city_code.label("city_code"),
            func.count(Occurrence.id).label("count"),
        )
        qb.base_join("health_unit")
        qb.apply_filters(f)
        qb.group_by(HealthUnit.city_code)
        qb.stmt = qb.stmt.order_by(func.count(Occurrence.id).desc())
        rows = await qb.execute()

        if not rows:
            return {
                "available": False,
                "message": (
                    f"Nenhum dado por municipio encontrado para '{disease_acronym}'."
                ),
            }

        municipalities = [
            {
                "city_code": r.city_code or "nao_informado",
                "cases": int(r.count),
            }
            for r in rows
        ]

        total_cases = sum(m["cases"] for m in municipalities)

        return {
            "available": True,
            "disease_code": disease_acronym.upper(),
            "by_municipality": municipalities[:20],
            "total_municipalities": len(municipalities),
            "total_cases": total_cases,
        }
