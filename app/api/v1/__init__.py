from fastapi import APIRouter

from .routes import vendors, buyers, agents, datasets, auth, acid, tide

router = APIRouter()
router.include_router(vendors.router)
router.include_router(buyers.router)
router.include_router(agents.router)
router.include_router(datasets.router)
router.include_router(auth.router)
router.include_router(acid.router)
router.include_router(tide.router)


__all__ = ["router"]

