import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["total_documents"] >= 5
        assert data["total_indexed_chunks"] > 0


@pytest.mark.asyncio
async def test_chat_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/chat",
            json={"message": "What are the shipping options and delivery times?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert len(data["sources"]) > 0
        assert data["insufficient_context"] is False


@pytest.mark.asyncio
async def test_admin_auth_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Invalid credentials
        bad_login = await client.post(
            "/api/admin/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        assert bad_login.status_code == 401

        # Valid credentials
        good_login = await client.post(
            "/api/admin/login",
            json={"username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD}
        )
        assert good_login.status_code == 200
        token = good_login.json()["access_token"]
        assert token != ""

        # Access protected endpoint with token
        headers = {"Authorization": f"Bearer {token}"}
        stats_resp = await client.get("/api/admin/stats", headers=headers)
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert stats["total_documents"] >= 5

        # Access protected endpoint without token should return 401
        unauth_resp = await client.get("/api/admin/stats")
        assert unauth_resp.status_code == 401


@pytest.mark.asyncio
async def test_upload_invalid_extension():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login = await client.post(
            "/api/admin/login",
            json={"username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        files = {"file": ("malicious.exe", b"binarycontent", "application/octet-stream")}
        upload_resp = await client.post("/api/documents/upload", files=files, headers=headers)
        assert upload_resp.status_code == 400
        assert "not supported" in upload_resp.json()["detail"]
