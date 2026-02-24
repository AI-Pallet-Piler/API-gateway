# Test script for authentication endpoints
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from gateway.main import app

client = TestClient(app)

# Base path for auth endpoints (includes API version prefix)
AUTH_BASE = "/api/v1/auth"


class MockResponse:
    """Mock response for httpx async client"""
    def __init__(self, content: bytes, status_code: int = 200, headers: dict = None):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {"content-type": "application/json"}

    def json(self):
        import json
        return json.loads(self.content)


# ============== LOGIN TESTS ==============

def test_login_success():
    """Test successful email/password login"""
    mock_response = MockResponse(
        content=b'{"access_token": "test_token", "token_type": "bearer"}',
        status_code=200
    )
    
    with patch("gateway.routes.auth.client.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        response = client.post(
            f"{AUTH_BASE}/login",
            json={"email": "user@example.com", "password": "password123"}
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    mock_response = MockResponse(
        content=b'{"detail": "Invalid credentials"}',
        status_code=401
    )
    
    with patch("gateway.routes.auth.client.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        response = client.post(
            f"{AUTH_BASE}/login",
            json={"email": "user@example.com", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401


def test_login_missing_fields():
    """Test login with missing required fields"""
    mock_response = MockResponse(
        content=b'{"detail": "Email and password required"}',
        status_code=422
    )
    
    with patch("gateway.routes.auth.client.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        response = client.post(f"{AUTH_BASE}/login", json={"email": "user@example.com"})
        
        assert response.status_code == 422


# ============== BADGE LOGIN TESTS ==============

def test_badge_login_success():
    """Test successful badge-based login"""
    mock_response = MockResponse(
        content=b'{"access_token": "badge_token", "token_type": "bearer", "user": {"name": "Picker 1"}}',
        status_code=200
    )
    
    with patch("gateway.routes.auth.client.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        response = client.post(
            f"{AUTH_BASE}/login-badge",
            json={"badge_id": "BADGE12345"}
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()


def test_badge_login_invalid_badge():
    """Test badge login with unknown badge ID"""
    mock_response = MockResponse(
        content=b'{"detail": "Badge not found"}',
        status_code=404
    )
    
    with patch("gateway.routes.auth.client.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        response = client.post(
            f"{AUTH_BASE}/login-badge",
            json={"badge_id": "INVALID_BADGE"}
        )
        
        assert response.status_code == 404


# ============== TOKEN REFRESH TESTS ==============

def test_refresh_token_success():
    """Test successful token refresh"""
    mock_response = MockResponse(
        content=b'{"access_token": "new_token", "token_type": "bearer"}',
        status_code=200
    )
    
    with patch("gateway.routes.auth.client.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        response = client.post(
            f"{AUTH_BASE}/refresh",
            json={"refresh_token": "valid_refresh_token"}
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()


def test_refresh_token_expired():
    """Test refresh with expired refresh token"""
    mock_response = MockResponse(
        content=b'{"detail": "Refresh token expired"}',
        status_code=401
    )
    
    with patch("gateway.routes.auth.client.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        response = client.post(
            f"{AUTH_BASE}/refresh",
            json={"refresh_token": "expired_token"}
        )
        
        assert response.status_code == 401


# ============== LOGOUT TESTS ==============

def test_logout_success():
    """Test successful logout"""
    mock_response = MockResponse(
        content=b'{"message": "Successfully logged out"}',
        status_code=200
    )
    
    with patch("gateway.routes.auth.client.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        response = client.post(
            f"{AUTH_BASE}/logout",
            json={"access_token": "valid_token"}
        )
        
        assert response.status_code == 200


# ============== TOKEN VALIDATION TESTS ==============

def test_validate_token_valid():
    """Test validation of a valid token"""
    mock_response = MockResponse(
        content=b'{"valid": true, "user_id": 1, "expires_at": "2026-02-25T00:00:00Z"}',
        status_code=200
    )
    
    with patch("gateway.routes.auth.client.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        response = client.post(
            f"{AUTH_BASE}/validate",
            json={"access_token": "valid_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True


def test_validate_token_invalid():
    """Test validation of an invalid token"""
    mock_response = MockResponse(
        content=b'{"valid": false, "detail": "Token is invalid or expired"}',
        status_code=401
    )
    
    with patch("gateway.routes.auth.client.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        response = client.post(
            f"{AUTH_BASE}/validate",
            json={"access_token": "invalid_token"}
        )
        
        assert response.status_code == 401


# ============== ERROR HANDLING TESTS ==============

def test_login_service_unavailable():
    """Test login when security service is unavailable"""
    import httpx
    
    with patch("gateway.routes.auth.client.request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = httpx.RequestError("Connection refused")
        
        response = client.post(
            f"{AUTH_BASE}/login",
            json={"email": "user@example.com", "password": "password123"}
        )
        
        assert response.status_code == 500
        assert "Authentication service error" in response.json()["detail"]
