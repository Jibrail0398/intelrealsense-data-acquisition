import os
import tempfile
import time
from pathlib import Path

import pytest

# Configure before the app (and its engine) is imported.
_TMP = Path(tempfile.mkdtemp(prefix="rs-collector-test-"))
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP / 'test.db'}"
os.environ["CAMERA_BACKEND"] = "mock"
os.environ["CAMERA_AUTO_CONNECT"] = "true"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        deadline = time.monotonic() + 10
        while c.get("/api/v1/camera/status").json()["status"] != "connected":
            if time.monotonic() > deadline:
                raise RuntimeError("mock camera did not connect")
            time.sleep(0.1)
        yield c


@pytest.fixture
def dest(tmp_path: Path) -> Path:
    return tmp_path / "dataset"


@pytest.fixture
def project(client, dest):
    name = f"Project {time.monotonic_ns()}"
    res = client.post("/api/v1/projects", json={
        "name": name,
        "destination_dir": str(dest),
        "formats": ["png", "jpg", "png16", "npy", "tiff"],
        "classes": ["stunting", "tidak stunting"],
    })
    assert res.status_code == 201, res.text
    return res.json()
