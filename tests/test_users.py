# Test script for user endpoints
from fastapi.testclient import TestClient
from gateway.main import app
import httpx
import pytest

client = TestClient(app)


class DummyResponse:
    """Mock response for httpx client"""
    def __init__(self, json_data, status_code=200, headers=None):
        self._json = json_data
        self.status_code = status_code
        self.headers = headers or {"content-type": "application/json"}

    def json(self):
        return self._json


class DummyBytesResponse:
    """Mock response that returns bytes content"""
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code
        self.headers = {"content-type": "application/json"}

    def json(self):
        import json
        return json.loads(self.content)


# Test for POST /users/create endpoint
def test_create_user_post(monkeypatch):
    """Test creating a user using POST method"""
    user_data = {"name": "Test User", "email": "test@example.com"}
    
    def fake_post(*args, **kwargs):
        return DummyBytesResponse(b'{"id": 1, "name": "Test User", "email": "test@example.com"}', 201)
    
    monkeypatch.setattr(httpx.Client, "request", fake_post)
    
    resp = client.post(
        "/users/create",
        json=user_data,
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 201
    assert "id" in resp.json()


def test_create_user_put(monkeypatch):
    """Test creating a user using PUT method"""
    user_data = {"name": "Test User", "email": "test@example.com"}
    
    def fake_put(*args, **kwargs):
        return DummyBytesResponse(b'{"id": 1, "name": "Test User", "email": "test@example.com"}', 200)
    
    monkeypatch.setattr(httpx.Client, "request", fake_put)
    
    resp = client.put(
        "/users/create",
        json=user_data,
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 200


def test_get_user(monkeypatch):
    """Test getting a user"""
    user_data = [{"id": 1, "name": "Test User", "email": "test@example.com"}]
    
    def fake_get(*args, **kwargs):
        return DummyBytesResponse(b'{"id": 1, "name": "Test User", "email": "test@example.com"}', 200)
    
    monkeypatch.setattr(httpx.Client, "request", fake_get)
    
    resp = client.get("/users/get")
    assert resp.status_code == 200


def test_delete_user(monkeypatch):
    """Test deleting a user"""
    def fake_delete(*args, **kwargs):
        return DummyBytesResponse(b'', 204)
    
    monkeypatch.setattr(httpx.Client, "request", fake_delete)
    
    resp = client.delete("/users/delete")
    assert resp.status_code == 204


def test_update_user(monkeypatch):
    """Test updating a user using PATCH"""
    update_data = {"name": "Updated User"}
    
    def fake_patch(*args, **kwargs):
        return DummyBytesResponse(b'{"id": 1, "name": "Updated User", "email": "test@example.com"}', 200)
    
    monkeypatch.setattr(httpx.Client, "request", fake_patch)
    
    resp = client.patch(
        "/users/update",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 200


def test_replace_user(monkeypatch):
    """Test replacing a user using PUT"""
    user_data = {"id": 1, "name": "Replaced User", "email": "replaced@example.com"}
    
    def fake_put(*args, **kwargs):
        return DummyBytesResponse(b'{"id": 1, "name": "Replaced User", "email": "replaced@example.com"}', 200)
    
    monkeypatch.setattr(httpx.Client, "request", fake_put)
    
    resp = client.put(
        "/users/replace",
        json=user_data,
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 200


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
