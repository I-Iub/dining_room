from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas import UserIn, UserOut
from src.db.database import get_session
from src.services.base import create_user
router = APIRouter()


@router.post('/users',
             response_model=UserOut,
             status_code=status.HTTP_201_CREATED,
             summary='Добавить пользователя',
             description='Метод принимает в теле запроса строку с ФИО пользователя для '
                         'возвращает присвоенный ему uuid')
async def add_user(user: UserIn,
                   session: AsyncSession = Depends(get_session)
                   ) -> Any:
    return await create_user(user.name, session)
