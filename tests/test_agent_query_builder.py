from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repository.query.agent_builder import AgentQueryBuilder


def _make_mock_session(rows):
    """Create a mock AsyncSession that returns the given rows."""
    mock_result = MagicMock()
    mock_result.all.return_value = rows

    session = AsyncMock()
    session.execute.return_value = mock_result
    return session


def _row(**kwargs):
    """Create a mock row object with named attributes."""
    obj = MagicMock()
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


class TestListDiseases:
    @pytest.mark.asyncio
    async def test_returns_diseases(self):
        rows = [
            _row(acronym="DENG", name="Dengue"),
            _row(acronym="CHIK", name="Chikungunya"),
        ]
        session = _make_mock_session(rows)
        builder = AgentQueryBuilder(session)

        result = await builder.list_diseases()

        assert len(result) == 2
        assert result[0] == {"acronym": "DENG", "name": "Dengue"}
        assert result[1] == {"acronym": "CHIK", "name": "Chikungunya"}

    @pytest.mark.asyncio
    async def test_returns_empty_list(self):
        session = _make_mock_session([])
        builder = AgentQueryBuilder(session)

        result = await builder.list_diseases()
        assert result == []


class TestGetTrend:
    @pytest.mark.asyncio
    async def test_returns_trend_data(self):
        rows = [
            _row(year=2023, month=1, cases=100),
            _row(year=2023, month=2, cases=200),
            _row(year=2023, month=3, cases=150),
        ]
        session = _make_mock_session(rows)
        builder = AgentQueryBuilder(session)

        result = await builder.get_trend("DENG")

        assert result["available"] is True
        assert result["disease_code"] == "DENG"
        assert result["total_periods"] == 3
        assert result["total_cases"] == 450
        assert result["max_cases"] == 200
        assert result["max_cases_date"] == "2023-02"
        assert result["min_cases"] == 100
        assert len(result["recent_periods"]) == 3

    @pytest.mark.asyncio
    async def test_no_data_returns_unavailable(self):
        session = _make_mock_session([])
        builder = AgentQueryBuilder(session)

        result = await builder.get_trend("DENG")

        assert result["available"] is False
        assert "message" in result


class TestGetSeasonality:
    @pytest.mark.asyncio
    async def test_returns_seasonality_data(self):
        rows = [
            _row(month=1, cases=100, num_years=2),
            _row(month=2, cases=300, num_years=2),
            _row(month=3, cases=50, num_years=2),
        ]
        session = _make_mock_session(rows)
        builder = AgentQueryBuilder(session)

        result = await builder.get_seasonality("DENG")

        assert result["available"] is True
        assert len(result["monthly_averages"]) == 3
        assert result["peak_month"] == "Fevereiro"
        assert result["low_month"] == "Marco"
        assert len(result["high_season"]) > 0
        assert len(result["low_season"]) > 0

    @pytest.mark.asyncio
    async def test_no_data_returns_unavailable(self):
        session = _make_mock_session([])
        builder = AgentQueryBuilder(session)

        result = await builder.get_seasonality("DENG")

        assert result["available"] is False


class TestGetDemographics:
    @pytest.mark.asyncio
    async def test_returns_demographic_data(self):
        sex_rows = [_row(sex="m", count=60), _row(sex="f", count=40)]
        age_row = _row(avg_age=35.5, min_age=5, max_age=80, total=100)
        evo_rows = [_row(evolution="1", count=70), _row(evolution="2", count=30)]

        session = AsyncMock()
        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            result = MagicMock()
            if call_count == 1:
                result.all.return_value = sex_rows
            elif call_count == 2:
                result.all.return_value = [age_row]
            else:
                result.all.return_value = evo_rows
            return result

        session.execute = mock_execute
        builder = AgentQueryBuilder(session)

        result = await builder.get_demographics("DENG")

        assert result["available"] is True
        assert result["total_cases"] == 100
        assert result["sex_distribution"] == {"m": 60, "f": 40}
        assert result["age_stats"]["avg"] == 35.5
        assert result["age_stats"]["min"] == 5
        assert result["age_stats"]["max"] == 80
        assert result["evolution_distribution"] == {"1": 70, "2": 30}

    @pytest.mark.asyncio
    async def test_no_data_returns_unavailable(self):
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.all.return_value = []
        session.execute.return_value = result_mock

        builder = AgentQueryBuilder(session)

        result = await builder.get_demographics("DENG")

        assert result["available"] is False


class TestGetGeographicDistribution:
    @pytest.mark.asyncio
    async def test_returns_geographic_data(self):
        dist_rows = [
            _row(district="Centro", count=50),
            _row(district="Norte", count=30),
        ]
        unit_rows = [
            _row(unit_name="UBS Centro", district="Centro", count=30),
            _row(unit_name="UBS Norte", district="Norte", count=20),
        ]

        session = AsyncMock()
        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            result = MagicMock()
            if call_count == 1:
                result.all.return_value = dist_rows
            else:
                result.all.return_value = unit_rows
            return result

        session.execute = mock_execute
        builder = AgentQueryBuilder(session)

        result = await builder.get_geographic_distribution("DENG")

        assert result["available"] is True
        assert len(result["by_district"]) == 2
        assert result["by_district"][0]["district"] == "Centro"
        assert len(result["top_health_units"]) == 2
        assert result["total_districts"] == 2

    @pytest.mark.asyncio
    async def test_no_data_returns_unavailable(self):
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.all.return_value = []
        session.execute.return_value = result_mock

        builder = AgentQueryBuilder(session)

        result = await builder.get_geographic_distribution("DENG")

        assert result["available"] is False
