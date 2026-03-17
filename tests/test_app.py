from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


def test_discover_page_loads() -> None:
    with TestClient(app) as client:
        response = client.get("/discover")
        assert response.status_code == 200
        assert "CharaSeed" in response.text
