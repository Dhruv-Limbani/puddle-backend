from fastapi import APIRouter

from .routes import vendors, buyers, agents, datasets, dataset_columns, auth, chats, chat_messages

router = APIRouter()
router.include_router(vendors.router)
router.include_router(buyers.router)
router.include_router(agents.router)
router.include_router(datasets.router)
router.include_router(dataset_columns.router)
router.include_router(auth.router)
router.include_router(chats.router)
router.include_router(chat_messages.router)

__all__ = ["router"]
