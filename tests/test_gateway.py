# python
from fastapi.testclient import TestClient
from gateway.main import app
import httpx

client = TestClient(app)

class DummyResponse:
    def __init__(self, json_data):
        self._json = json_data
        self.status_code = 200
        self.headers = {"content-type": "application/json"}

    def json(self):
        return self._json

def test_get_first_users(monkeypatch):
    users = [{"name": "Leanne Graham", "email": "Sincere@april.biz"}]

    def fake_get():
        return DummyResponse(users)

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    resp = client.get("/get_first users")
    assert resp.status_code == 200
    assert resp.json() == {"name": "Leanne Graham", "email": "Sincere@april.biz"}

def test_favicon_returns_ok():
    resp = client.get("/favicon.ico")
    assert resp.status_code == 200
