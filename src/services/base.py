import io
from typing import Any
from datetime import datetime, timezone
from uuid import UUID, uuid4

from aioshutil import copyfileobj
from fastapi import Response, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete, insert, select

from src.db.database import Base
from src.services.qr import read_image
from src.api.v1.schemas import TicketUUID, UserUUID
from src.models.users import Ticket, User
from src.services.qr import get_image
from src.services.utils import is_valid_uuid


async def create_user(name: str, session: AsyncSession) -> dict[str, str]:
    user_uuid = uuid4()
    user = [dict(name=name, uuid=user_uuid)]
    statement = (
        insert(User).values(user)
    )
    await session.execute(statement)
    await session.commit()
    return {'name': name, 'uuid': user_uuid.hex}


async def user_delete(user: UserUUID, session: AsyncSession) -> Response:
    is_exists = await is_uuid_exists(user.uuid, User, session)
    if not is_exists:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    statement = delete(User).where(User.uuid == user.uuid)
    await session.execute(statement)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def create_ticket(user: UserUUID, session: AsyncSession) -> dict[str, Any] | Response:
    is_exists = await is_uuid_exists(user.uuid, User, session)
    if not is_exists:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    ticket_uuid = uuid4()
    created = datetime.now(timezone.utc)
    ticket = [dict(uuid=ticket_uuid, created=created, user_uuid=user.uuid.hex)]
    statement = insert(Ticket).values(ticket)
    try:
        await session.execute(statement)
    except IntegrityError as error:
        if 'UNIQUE constraint failed: tickets.user_uuid' not in str(error):
            raise
        return Response(status_code=status.HTTP_409_CONFLICT, content='User ticket already exist')

    await session.commit()
    return {'uuid': ticket_uuid, 'created': created, 'user_uuid': user.uuid}


async def retrieve_tickets(session: AsyncSession) -> list[dict[str, Any]]:
    result = await session.execute(select(Ticket))
    tickets = [ticket.__dict__ for ticket, *_ in result.all()]
    return tickets


async def ticket_delete(ticket: TicketUUID, session: AsyncSession) -> Response:
    statement = select(Ticket).where(Ticket.uuid == ticket.uuid)
    result = await session.execute(statement)
    if result.first() is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    statement = delete(Ticket).where(Ticket.uuid == ticket.uuid)
    await session.execute(statement)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def is_uuid_exists(instance_uuid: UUID, model: Base, session: AsyncSession) -> bool:
    statement = select(model).where(model.uuid == instance_uuid)
    result = await session.execute(statement)
    if result.first() is None:
        return False
    return True


async def create_qr(ticket: TicketUUID, session: AsyncSession) -> Response:
    is_exists = is_uuid_exists(ticket.uuid, Ticket, session)
    if not is_exists:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    try:
        img = get_image(str(ticket))
    except IndexError:
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                               content={'error': 'Ошибка сервера. Не удалось создать QR-код.'})
    file = io.BytesIO()
    img.save(file, 'png')
    return Response(content=file.getvalue(), media_type="image/png")


async def qr_check(file: UploadFile, session: AsyncSession) -> Response:
    buffer = io.BytesIO()
    await copyfileobj(file.file, buffer)
    buffer.seek(0)
    data = read_image(buffer)
    if not is_valid_uuid(data):
        return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content='Информация на QR-коде не является UUID')
    ticket_uuid = UUID(data)
    is_exists = await is_uuid_exists(ticket_uuid, Ticket, session)
    if not is_exists:
        return Response(status_code=status.HTTP_404_NOT_FOUND,
                        content='Купон не найден')
    return Response(status_code=status.HTTP_200_OK,
                    content='Приятного аппетита!')
