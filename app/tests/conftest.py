import asyncio
import os
import pytest
from typing import AsyncGenerator, Dict

from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.config import settings
from app.core.db import engine, AsyncSessionLocal, Base
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop that will be used for the whole test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def app_init():
    """Initialize app setup - database tables etc."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(app_init) -> AsyncGenerator:
    """Get a fresh database session for each test."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Get an async client for testing the FastAPI endpoints.
    
    Uses TestClient under the hood which properly wraps the app for testing.
    """
    async with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_vendor_data() -> Dict:
    """Sample vendor data for tests."""
    return {
        "name": "Test Data Corp",
        "industry_focus": "Technology",
        "description": "Provider of test datasets",
        "contact_email": "test@example.com",
        "contact_phone": "+1-555-0123",
        "website_url": "https://test.example.com",
        "country": "US",
        "region": "West",
        "city": "San Francisco",
        "organization_type": "Corporation"
    }


@pytest.fixture
def sample_dataset_data(sample_vendor_data) -> Dict:
    """Sample dataset data for tests."""
    return {
        "title": "Test Dataset",
        "description": "A dataset for testing",
        "domain": "Testing",
        "dataset_type": "Tabular",
        "visibility": "public",
        "topics": ["testing", "quality assurance"],
        "entities": ["test_cases", "results"],
        "columns": [
            {
                "name": "test_id",
                "description": "Unique test identifier",
                "data_type": "uuid"
            },
            {
                "name": "test_name",
                "description": "Name of the test case",
                "data_type": "text"
            }
        ]
    }


@pytest.fixture
def sample_buyer_data() -> Dict:
    """Sample buyer data for tests."""
    return {
        "name": "John Tester",
        "organization": "Test Labs Inc",
        "contact_email": "john@testlabs.com",
        "industry": "Quality Assurance",
        "use_case_focus": "Automated Testing",
        "country": "US",
        "job_title": "Test Engineer"
    }


@pytest.fixture
def sample_agent_data() -> Dict:
    """Sample agent data for tests."""
    return {
        "name": "Test Embedding Agent",
        "description": "Agent for test data processing",
        "model_used": "gemini-embedding-001",
        "config": {
            "batch_size": 32,
            "compute_stats": True
        },
        "active": True
    }
