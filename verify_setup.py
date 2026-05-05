import asyncio
from httpx import AsyncClient, ASGITransport
from main import app

async def verify():
    print("Verifying root endpoint...")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    print("\nVerifying health endpoint...")
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

if __name__ == "__main__":
    asyncio.run(verify())
