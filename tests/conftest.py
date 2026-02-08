import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.db.redis_client import _in_memory_cache


@pytest.fixture(autouse=True)
def reset_in_memory_cache():
    _in_memory_cache.flushall()
    yield
    _in_memory_cache.flushall()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
