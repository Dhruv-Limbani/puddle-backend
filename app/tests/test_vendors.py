import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import vendors as crud_vendors


@pytest.mark.asyncio
async def test_create_vendor(
    async_client: AsyncClient,
    db_session: AsyncSession,
    sample_vendor_data: dict,
):
    """Test vendor creation endpoint."""
    response = await async_client.post("/api/v1/vendors/", json=sample_vendor_data)
    assert response.status_code == 201
    data = response.json()
    
    # Check required fields
    assert data["id"] is not None
    assert data["name"] == sample_vendor_data["name"]
    assert data["industry_focus"] == sample_vendor_data["industry_focus"]
    
    # Verify in database
    db_vendor = await crud_vendors.get_vendor(db_session, data["id"])
    assert db_vendor is not None
    assert db_vendor.name == sample_vendor_data["name"]


@pytest.mark.asyncio
async def test_get_vendor(
    async_client: AsyncClient,
    db_session: AsyncSession,
    sample_vendor_data: dict,
):
    """Test retrieving a vendor by ID."""
    # Create vendor first
    vendor = await crud_vendors.create_vendor(db_session, sample_vendor_data)
    await db_session.commit()
    
    # Get vendor
    response = await async_client.get(f"/api/v1/vendors/{vendor.id}")
    assert response.status_code == 200
    data = response.json()
    
    # Check data
    assert data["id"] == str(vendor.id)  # UUID comes back as string
    assert data["name"] == vendor.name
    assert data["industry_focus"] == vendor.industry_focus


@pytest.mark.asyncio
async def test_list_vendors(
    async_client: AsyncClient,
    db_session: AsyncSession,
    sample_vendor_data: dict,
):
    """Test listing vendors with pagination."""
    # Create multiple vendors
    vendor_names = ["Vendor A", "Vendor B", "Vendor C"]
    for name in vendor_names:
        data = sample_vendor_data.copy()
        data["name"] = name
        await crud_vendors.create_vendor(db_session, data)
    await db_session.commit()
    
    # Test pagination
    response = await async_client.get("/api/v1/vendors/?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Get next page
    response = await async_client.get("/api/v1/vendors/?limit=2&offset=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0  # At least vendor C should be there


@pytest.mark.asyncio
async def test_update_vendor(
    async_client: AsyncClient,
    db_session: AsyncSession,
    sample_vendor_data: dict,
):
    """Test updating vendor information."""
    # Create vendor
    vendor = await crud_vendors.create_vendor(db_session, sample_vendor_data)
    await db_session.commit()
    
    # Update fields
    update_data = {
        "description": "Updated description",
        "contact_email": "updated@example.com"
    }
    response = await async_client.put(
        f"/api/v1/vendors/{vendor.id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check updates
    assert data["description"] == update_data["description"]
    assert data["contact_email"] == update_data["contact_email"]
    # Original data should be unchanged
    assert data["name"] == sample_vendor_data["name"]


@pytest.mark.asyncio
async def test_delete_vendor(
    async_client: AsyncClient,
    db_session: AsyncSession,
    sample_vendor_data: dict,
):
    """Test vendor deletion."""
    # Create vendor
    vendor = await crud_vendors.create_vendor(db_session, sample_vendor_data)
    await db_session.commit()
    
    # Delete vendor
    response = await async_client.delete(f"/api/v1/vendors/{vendor.id}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True
    
    # Verify deletion
    db_vendor = await crud_vendors.get_vendor(db_session, vendor.id)
    assert db_vendor is None


@pytest.mark.asyncio
async def test_vendor_not_found(
    async_client: AsyncClient,
):
    """Test 404 responses for non-existent vendor."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    
    # GET should 404
    response = await async_client.get(f"/api/v1/vendors/{fake_id}")
    assert response.status_code == 404
    
    # PUT should 404
    response = await async_client.put(
        f"/api/v1/vendors/{fake_id}",
        json={"name": "New Name"}
    )
    assert response.status_code == 404
    
    # DELETE should 404
    response = await async_client.delete(f"/api/v1/vendors/{fake_id}")
    assert response.status_code == 404