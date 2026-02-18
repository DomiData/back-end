import json
from pathlib import Path

import pandas as pd


DISEASE_CODE_MAP = {
    "dengue": "DENG",
    "chikungunya": "CHIK",
    "zika": "ZIKA",
}


def _find_disease_dir(disease_code: str, data_dir: str) -> Path | None:
    """Find the most recent output directory for a disease code."""
    base = Path(data_dir)
    if not base.exists():
        return None

    matches = sorted(
        [d for d in base.iterdir() if d.is_dir() and d.name.startswith(disease_code)],
        key=lambda d: d.name,
        reverse=True,
    )
    return matches[0] if matches else None


def _resolve_disease_code(disease_name: str) -> str:
    """Resolve a disease name (PT-BR or code) to the output directory prefix."""
    name_lower = disease_name.lower().strip()
    if name_lower in DISEASE_CODE_MAP:
        return DISEASE_CODE_MAP[name_lower]
    # Already a code like DENG, CHIK, etc.
    return name_lower.upper()


def list_available_diseases(data_dir: str) -> list[dict]:
    """List diseases that have prediction data available."""
    base = Path(data_dir)
    if not base.exists():
        return []

    diseases = {}
    for d in base.iterdir():
        if d.is_dir():
            # Extract disease code from dir name like DENG_UF25_20251211_161625
            parts = d.name.split("_")
            if parts:
                code = parts[0]
                if code not in diseases:
                    diseases[code] = d.name

    reverse_map = {v: k for k, v in DISEASE_CODE_MAP.items()}
    return [
        {"code": code, "name": reverse_map.get(code, code), "directory": dirname}
        for code, dirname in diseases.items()
    ]


def load_time_series(disease_name: str, data_dir: str) -> dict:
    """Load time series data for a disease. Returns summary with key statistics."""
    code = _resolve_disease_code(disease_name)
    disease_dir = _find_disease_dir(code, data_dir)

    if not disease_dir:
        return {
            "available": False,
            "message": f"Nenhum dado de serie temporal encontrado para '{disease_name}'.",
        }

    csv_path = disease_dir / "time_series.csv"
    if not csv_path.exists():
        return {
            "available": False,
            "message": f"Arquivo time_series.csv nao encontrado para '{disease_name}'.",
        }

    df = pd.read_csv(csv_path, parse_dates=["date"])

    total_cases = int(df["cases"].sum())
    mean_cases = round(float(df["cases"].mean()), 1)
    max_cases = int(df["cases"].max())
    max_date = df.loc[df["cases"].idxmax(), "date"].strftime("%Y-%m")
    min_cases = int(df["cases"].min())
    date_range_start = df["date"].min().strftime("%Y-%m")
    date_range_end = df["date"].max().strftime("%Y-%m")

    # Recent trend (last 6 periods)
    recent = df.tail(6)
    recent_data = [
        {"date": row["date"].strftime("%Y-%m"), "cases": int(row["cases"])}
        for _, row in recent.iterrows()
    ]

    return {
        "available": True,
        "disease": disease_name,
        "disease_code": code,
        "total_periods": len(df),
        "date_range": f"{date_range_start} a {date_range_end}",
        "total_cases": total_cases,
        "mean_monthly_cases": mean_cases,
        "max_cases": max_cases,
        "max_cases_date": max_date,
        "min_cases": min_cases,
        "recent_periods": recent_data,
    }


def load_forecast(disease_name: str, data_dir: str) -> dict:
    """Load forecast data for a disease."""
    code = _resolve_disease_code(disease_name)
    disease_dir = _find_disease_dir(code, data_dir)

    if not disease_dir:
        return {
            "available": False,
            "message": f"Nenhum dado de previsao encontrado para '{disease_name}'.",
        }

    csv_path = disease_dir / "forecast.csv"
    if not csv_path.exists():
        return {
            "available": False,
            "message": f"Arquivo forecast.csv nao encontrado para '{disease_name}'.",
        }

    df = pd.read_csv(csv_path, parse_dates=["date"])

    forecasts = [
        {
            "date": row["date"].strftime("%Y-%m"),
            "predicted_cases": round(float(row["predicted_cases"]), 1),
            "model": row["model"],
        }
        for _, row in df.iterrows()
    ]

    # Load metrics if available
    metrics = load_metrics(data_dir, code)

    return {
        "available": True,
        "disease": disease_name,
        "disease_code": code,
        "forecast_periods": len(df),
        "forecasts": forecasts,
        "model_metrics": metrics.get("metrics", {}),
        "best_model": metrics.get("best_model", ""),
    }


def load_metrics(data_dir: str, disease_code: str | None = None) -> dict:
    """Load model performance metrics."""
    if disease_code:
        disease_dir = _find_disease_dir(disease_code, data_dir)
    else:
        # Try first available directory
        base = Path(data_dir)
        dirs = [d for d in base.iterdir() if d.is_dir()] if base.exists() else []
        disease_dir = dirs[0] if dirs else None

    if not disease_dir:
        return {"available": False, "metrics": {}}

    metrics_path = disease_dir / "metrics.json"
    if not metrics_path.exists():
        return {"available": False, "metrics": {}}

    with open(metrics_path) as f:
        metrics = json.load(f)

    # Determine best model by lowest RMSE
    best_model = ""
    best_rmse = float("inf")
    for model_name, model_metrics in metrics.items():
        rmse = model_metrics.get("RMSE", float("inf"))
        if rmse < best_rmse:
            best_rmse = rmse
            best_model = model_name

    return {
        "available": True,
        "metrics": metrics,
        "best_model": best_model,
    }


def get_seasonality_summary(disease_name: str, data_dir: str) -> dict:
    """Compute monthly averages from time series to identify seasonal patterns."""
    code = _resolve_disease_code(disease_name)
    disease_dir = _find_disease_dir(code, data_dir)

    if not disease_dir:
        return {
            "available": False,
            "message": f"Nenhum dado de sazonalidade encontrado para '{disease_name}'.",
        }

    csv_path = disease_dir / "time_series.csv"
    if not csv_path.exists():
        return {
            "available": False,
            "message": f"Arquivo time_series.csv nao encontrado para '{disease_name}'.",
        }

    df = pd.read_csv(csv_path, parse_dates=["date"])

    month_names_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }

    monthly_avg = df.groupby("month")["cases"].mean().round(1)
    monthly_data = [
        {"month": int(m), "month_name": month_names_pt[int(m)], "avg_cases": float(v)}
        for m, v in monthly_avg.items()
    ]

    # Identify peak and low months
    peak_month = monthly_avg.idxmax()
    low_month = monthly_avg.idxmin()

    # High season: months with above-average cases
    overall_avg = monthly_avg.mean()
    high_season_months = [
        month_names_pt[int(m)] for m, v in monthly_avg.items() if v > overall_avg
    ]
    low_season_months = [
        month_names_pt[int(m)] for m, v in monthly_avg.items() if v <= overall_avg
    ]

    return {
        "available": True,
        "disease": disease_name,
        "disease_code": code,
        "monthly_averages": monthly_data,
        "peak_month": month_names_pt[int(peak_month)],
        "peak_month_avg_cases": round(float(monthly_avg[peak_month]), 1),
        "low_month": month_names_pt[int(low_month)],
        "low_month_avg_cases": round(float(monthly_avg[low_month]), 1),
        "high_season": high_season_months,
        "low_season": low_season_months,
    }
