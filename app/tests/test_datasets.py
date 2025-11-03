import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from app.crud import datasets as crud_datasets, vendors as crud_vendors


@pytest.mark.asyncio
async def test_create_dataset_with_embedding(
    async_client: AsyncClient,
    db_session: AsyncSession,
    sample_vendor_data: dict,
    sample_dataset_data: dict,
):
    """Test dataset creation with automatic embedding generation."""
    # Create a vendor first
    vendor = await crud_vendors.create_vendor(db_session, sample_vendor_data)
    await db_session.commit()
    sample_dataset_data["vendor_id"] = str(vendor.id)
    
    # Mock the embedding generation to return a known vector
    mock_embedding = [0.1] * 1536  # 1536-d vector filled with 0.1
    with patch("app.utils.embedding_utils.generate_embedding", return_value=mock_embedding):
        response = await async_client.post("/api/v1/datasets/", json=sample_dataset_data)
    
    assert response.status_code == 201
    data = response.json()
    
    # Check core fields
    assert data["id"] is not None
    assert data["title"] == sample_dataset_data["title"]
    assert data["vendor_id"] == str(vendor.id)
    
    # Check embedding
    assert len(data["embedding"]) == 1536
    assert all(isinstance(x, float) for x in data["embedding"])


@pytest.mark.asyncio
async def test_dataset_search(
    async_client: AsyncClient,
    db_session: AsyncSession,
    sample_vendor_data: dict,
    sample_dataset_data: dict,
):
    """Test dataset similarity search."""
    # Create a vendor
    vendor = await crud_vendors.create_vendor(db_session, sample_vendor_data)
    await db_session.commit()
    sample_dataset_data["vendor_id"] = str(vendor.id)
    
    # Create multiple datasets with different embeddings
    mock_embeddings = {
        "ML Dataset": [0.9] * 1536,  # Very similar to search query
        "Test Dataset": [0.1] * 1536,  # Less similar
        "Random Dataset": [-0.5] * 1536,  # Least similar
    }
    
    for title, emb in mock_embeddings.items():
        data = sample_dataset_data.copy()
        data["title"] = title
        with patch("app.utils.embedding_utils.generate_embedding", return_value=emb):
            await async_client.post("/api/v1/datasets/", json=data)
    
    # Search with a query that should match "ML Dataset" best
    search_query = {"query": "machine learning", "top_k": 2}
    with patch("app.utils.embedding_utils.generate_embedding", return_value=[1.0] * 1536):
        response = await async_client.post("/api/v1/datasets/search/embedding", json=search_query)
    
    assert response.status_code == 200
    results = response.json()["results"]
    
    # Should return top 2 most similar
    assert len(results) == 2
    # First result should be "ML Dataset" (most similar)
    assert results[0]["title"] == "ML Dataset"
    # Results should be scored
    assert all("score" in r for r in results)
    assert all(0 <= r["score"] <= 1 for r in results)
    # Scores should be sorted descending
    assert results[0]["score"] >= results[1]["score"]


@pytest.mark.asyncio
async def test_dataset_crud(
    async_client: AsyncClient,
    db_session: AsyncSession,
    sample_vendor_data: dict,
    sample_dataset_data: dict,
):
    """Test basic dataset CRUD operations."""
    # Create vendor
    vendor = await crud_vendors.create_vendor(db_session, sample_vendor_data)
    await db_session.commit()
    sample_dataset_data["vendor_id"] = str(vendor.id)
    
    # Create dataset
    mock_embedding = [0.1] * 1536
    with patch("app.utils.embedding_utils.generate_embedding", return_value=mock_embedding):
        response = await async_client.post("/api/v1/datasets/", json=sample_dataset_data)
    assert response.status_code == 201
    dataset = response.json()
    
    # Get dataset
    response = await async_client.get(f"/api/v1/datasets/{dataset['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == sample_dataset_data["title"]
    
    # Update dataset
    update_data = {"description": "Updated description"}
    response = await async_client.put(f"/api/v1/datasets/{dataset['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"
    
    # Delete dataset
    response = await async_client.delete(f"/api/v1/datasets/{dataset['id']}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True
    
    # Verify deletion
    response = await async_client.get(f"/api/v1/datasets/{dataset['id']}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_dataset_column_operations(
    async_client: AsyncClient,
    db_session: AsyncSession,
    sample_vendor_data: dict,
    sample_dataset_data: dict,
):
    """Test dataset column creation and retrieval."""
    # Create vendor and dataset
    vendor = await crud_vendors.create_vendor(db_session, sample_vendor_data)
    await db_session.commit()
    sample_dataset_data["vendor_id"] = str(vendor.id)
    
    with patch("app.utils.embedding_utils.generate_embedding", return_value=[0.1] * 1536):
        response = await async_client.post("/api/v1/datasets/", json=sample_dataset_data)
    dataset = response.json()
    
    # Column info should be included in dataset creation
    assert "columns" in dataset
    assert len(dataset["columns"]) == len(sample_dataset_data["columns"])
    
    # Verify column details
    for i, col in enumerate(dataset["columns"]):
        assert col["name"] == sample_dataset_data["columns"][i]["name"]
        assert col["description"] == sample_dataset_data["columns"][i]["description"]
        assert col["data_type"] == sample_dataset_data["columns"][i]["data_type"]