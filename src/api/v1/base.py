from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Response, status
# from sqlalchemy.ext.asyncio import AsyncSession

# from src.api.v1.schemas import

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World"}
