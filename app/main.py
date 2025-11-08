from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.v1 import router as api_v1_router
from app.core.db import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist (useful for local dev)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Puddle Backend",
    description="""
    Puddle Backend API provides access to dataset marketplace functionality including:
    
    - Dataset catalog with vector similarity search
    - Vendor and buyer management
    - AI agent configurations
    - Column-level dataset metadata
    """,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "datasets",
            "description": "Dataset operations including vector similarity search",
        },
        {
            "name": "dataset-columns",
            "description": "Dataset column metadata and schema information",
        },
        {
            "name": "vendors",
            "description": "Dataset vendor/provider management",
        },
        {
            "name": "buyers",
            "description": "Dataset buyer/consumer management",
        },
        {
            "name": "agents",
            "description": "AI agent configurations for dataset processing",
        },
        {
            "name": "authentication",
            "description": "User registration and login",
        },
        {
            "name": "chats",
            "description": "Chat sessions between users and vendors",
        },
        {
            "name": "chat-messages",
            "description": "Messages within chat sessions",
        },
    ],
)

# Basic CORS - adjust origins as needed in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")