import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.utils import embedding_utils
from app.crud import vendors as crud_vendors


@pytest.mark.asyncio
async def test_dataset_search(
    async_client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch
):
    """Test dataset similarity search."""
    # Patch generate_embedding to deterministic vectors
    async def fake_embed(text: str):
        if "alpha" in text:
            v = [1.0] + [0.0] * 1535
        elif "beta" in text:
            v = [0.0, 1.0] + [0.0] * 1534
        else:
            v = [0.0] * 1536
        return v

    monkeypatch.setattr(embedding_utils, "generate_embedding", fake_embed)
    
    # Create a vendor first
    vendor = await crud_vendors.create_vendor(db_session, {"name": "SearchVendor"})
    await db_session.commit()

    # create two datasets with different embeddings
    r = await async_client.post("/api/v1/datasets/", json={
        "vendor_id": str(vendor.id),
        "title": "Alpha dataset",
        "description": "alpha dataset for testing"
    })
    assert r.status_code == 201
    
    r = await async_client.post("/api/v1/datasets/", json={
        "vendor_id": str(vendor.id),
        "title": "Beta dataset",
        "description": "beta dataset for testing"
    })
    assert r.status_code == 201

    # search for alpha-like query
    r = await async_client.post("/api/v1/datasets/search/embedding", json={
        "query": "alpha something",
        "top_k": 2
    })
    assert r.status_code == 200
    
    data = r.json()
    assert "results" in data
    assert len(data["results"]) == 2
    # top result should be Alpha dataset
    assert data["results"][0]["title"] == "Alpha dataset"
    # Results should be scored
    assert all("score" in r for r in data["results"])