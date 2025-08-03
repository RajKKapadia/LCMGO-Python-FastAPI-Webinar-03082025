from fastapi import APIRouter

router = APIRouter(prefix="/health")


@router.get("/status")
async def handle_get_status():
    return 200
