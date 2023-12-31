from typing import Any, Optional

from fastapi import APIRouter, Depends, Response, UploadFile, status
# from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas import MealIn, MealsOut, TicketOut, TicketUUID, UserIn, UserOut, UserUUID
from src.db.database import get_session
from src.services.base import (create_qr, create_ticket, create_user, meal_delete, create_meal, retrieve_tickets,
                               retrieve_meals, ticket_delete, user_delete)

router = APIRouter()


@router.post('/users',
             response_model=UserOut,
             status_code=status.HTTP_201_CREATED,
             summary='Добавить пользователя',
             description='Метод принимает в теле запроса строку с ФИО пользователя и '
                         'возвращает присвоенный ему uuid')
async def add_user(user: UserIn,
                   session: AsyncSession = Depends(get_session)
                   ) -> Any:
    return await create_user(user.name, session)


@router.delete('/users',
               response_model=None,
               status_code=status.HTTP_204_NO_CONTENT,
               summary='Удалить пользователя')
async def delete_user(user: UserUUID, session: AsyncSession = Depends(get_session)
                      ) -> Optional[Response]:
    return await user_delete(user, session)


@router.post('/tickets',
             response_model=TicketOut,
             status_code=status.HTTP_201_CREATED,
             summary='Получить QR-код для пользователя',
             description='Метод принимает в теле запроса строку с uuid пользователя и '
                         'возвращает присвоенный ему uuid купона на еду')
async def add_ticket(user: UserUUID,
                     session: AsyncSession = Depends(get_session)
                     ) -> Any:
    return await create_ticket(user, session)


@router.get('/tickets',
            response_model=list[TicketOut],
            status_code=status.HTTP_200_OK,
            summary='Информация о купонах.',
            description='Вернуть информацию о ранее созданных купонах.')
async def get_tickets(session: AsyncSession = Depends(get_session)) -> Any:
    return await retrieve_tickets(session)


@router.delete('/tickets',
               response_model=None,
               status_code=status.HTTP_204_NO_CONTENT,
               summary='Удалить купон на еду')
async def delete_ticket(ticket: TicketUUID, session: AsyncSession = Depends(get_session)
                        ) -> Any:
    return await ticket_delete(ticket, session)


@router.post('/qr',
             response_model=None,
             status_code=status.HTTP_200_OK,
             summary='Получить QR-код',
             description='Возвращает QR-код')
async def get_qr(ticket_uuid: TicketUUID, session: AsyncSession = Depends(get_session)) -> Response:
    return await create_qr(ticket_uuid, session)
    # todo: сделать StreamingResponse?
    # def iter_file(file_obj):
    #     yield from file_obj
    # return StreamingResponse(iter_file(payload), media_type='image/png')


@router.post('/meals',
             response_model=None,
             status_code=status.HTTP_200_OK,
             summary='Сделать отметку о приёме пищи',
             description='Проверяет что количество приёмов пищи не превышено и делает отметку о приёме пищи в БД')
async def add_meal(file: UploadFile, session: AsyncSession = Depends(get_session)) -> Response:
    return await create_meal(file, session)


@router.get('/meals',
            response_model=list[MealsOut],
            status_code=status.HTTP_200_OK,
            summary='Информация об отметках времени приёма пищи',
            description='Получить информацию об отметках времени приёма пищи')
async def get_meals(session: AsyncSession = Depends(get_session)) -> Any:
    return await retrieve_meals(session)


@router.delete('/meals',
               response_model=None,
               status_code=status.HTTP_204_NO_CONTENT,
               summary='Удалить отметку о приёме пищи')
async def delete_meal(meal: MealIn, session: AsyncSession = Depends(get_session)) -> Any:
    return await meal_delete(meal, session)
