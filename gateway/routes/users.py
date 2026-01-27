from fastapi import APIRouter, Response, status

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", tags=["users"])
async def users_root():
    return Response(status_code=status.HTTP_200_OK)