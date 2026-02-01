import pytest

from app.services.chat.data_loader import (
    get_seasonality_summary,
    list_available_diseases,
    load_forecast,
    load_metrics,
    load_time_series,
)


class TestLoadTimeSeries:
    def test_valid_data(self, prediction_data_dir):
        result = load_time_series("dengue", prediction_data_dir)
        assert result["available"] is True
        assert result["total_periods"] == 12
        assert result["date_range"] == "2020-01 a 2020-12"
        assert result["total_cases"] > 0
        assert result["max_cases"] == 1500
        assert result["max_cases_date"] == "2020-04"
        assert len(result["recent_periods"]) == 6

    def test_missing_directory(self, empty_data_dir):
        result = load_time_series("dengue", empty_data_dir)
        assert result["available"] is False
        assert "message" in result

    def test_nonexistent_disease(self, prediction_data_dir):
        result = load_time_series("malaria", prediction_data_dir)
        assert result["available"] is False

    def test_disease_code_resolution(self, prediction_data_dir):
        result = load_time_series("DENG", prediction_data_dir)
        assert result["available"] is True


class TestLoadForecast:
    def test_valid_data(self, prediction_data_dir):
        result = load_forecast("dengue", prediction_data_dir)
        assert result["available"] is True
        assert result["forecast_periods"] == 6
        assert len(result["forecasts"]) == 6
        assert result["forecasts"][0]["model"] == "Prophet"
        assert result["best_model"] == "Prophet"

    def test_missing_directory(self, empty_data_dir):
        result = load_forecast("dengue", empty_data_dir)
        assert result["available"] is False


class TestLoadMetrics:
    def test_valid_metrics(self, prediction_data_dir):
        result = load_metrics(prediction_data_dir, "DENG")
        assert result["available"] is True
        assert "ARIMA" in result["metrics"]
        assert "Prophet" in result["metrics"]
        assert result["best_model"] == "Prophet"

    def test_missing_metrics(self, empty_data_dir):
        result = load_metrics(empty_data_dir)
        assert result["available"] is False


class TestGetSeasonalitySummary:
    def test_valid_data(self, prediction_data_dir):
        result = get_seasonality_summary("dengue", prediction_data_dir)
        assert result["available"] is True
        assert len(result["monthly_averages"]) == 12
        assert result["peak_month"] is not None
        assert result["low_month"] is not None
        assert len(result["high_season"]) > 0
        assert len(result["low_season"]) > 0

    def test_peak_month_is_april(self, prediction_data_dir):
        """April has the highest cases (1500) in fixture data."""
        result = get_seasonality_summary("dengue", prediction_data_dir)
        assert result["peak_month"] == "Abril"

    def test_missing_directory(self, empty_data_dir):
        result = get_seasonality_summary("dengue", empty_data_dir)
        assert result["available"] is False


class TestListAvailableDiseases:
    def test_with_data(self, prediction_data_dir):
        result = list_available_diseases(prediction_data_dir)
        assert len(result) == 1
        assert result[0]["code"] == "DENG"
        assert result[0]["name"] == "dengue"

    def test_empty_directory(self, empty_data_dir):
        result = list_available_diseases(empty_data_dir)
        assert result == []

    def test_nonexistent_directory(self):
        result = list_available_diseases("/nonexistent/path")
        assert result == []
