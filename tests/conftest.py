import shutil
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def prediction_data_dir(tmp_path):
    """Create a temp prediction data directory with fixture files."""
    disease_dir = tmp_path / "DENG_UF25_test"
    disease_dir.mkdir()

    for filename in ["time_series.csv", "forecast.csv", "metrics.json"]:
        src = FIXTURES_DIR / filename
        if src.exists():
            shutil.copy(src, disease_dir / filename)

    return str(tmp_path)


@pytest.fixture
def empty_data_dir(tmp_path):
    """An empty temp directory with no prediction data."""
    return str(tmp_path)
