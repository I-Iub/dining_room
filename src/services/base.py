import io
from typing import Any
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete, insert, select

from src.api.v1.schemas import TicketUUID, UserUUID
from src.models.users import Ticket, User
from src.services.qr import get_image


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
    if not is_user_exists(user, session):
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    statement = delete(User).where(User.uuid == user.uuid)
    await session.execute(statement)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def create_ticket(user: UserUUID, session: AsyncSession) -> dict[str, Any] | Response:
    if not await is_user_exists(user, session):
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
    return {'uuid': ticket_uuid, 'created': created, 'user': user.uuid}


# get_ticket():
async def retrieve_tickets(session: AsyncSession) -> list[dict[str, Any]]:
    result = await session.execute(select(Ticket))
    # print(result.all())
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


async def is_user_exists(user: UserUUID, session: AsyncSession) -> bool:
    statement = select(User).where(User.uuid == user.uuid)
    result = await session.execute(statement)
    if result.first() is None:
        return False
    return True


async def create_qr(ticket: TicketUUID, session: AsyncSession) -> tuple[bool, io.BytesIO | Response]:
    statement = select(Ticket).where(Ticket.uuid == ticket.uuid)
    result = await session.execute(statement)
    is_exists = result.scalar()
    if not is_exists:
        return False, Response(status_code=status.HTTP_404_NOT_FOUND)
    try:
        img = get_image(str(ticket))
    except IndexError:
        return False, Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                               content={'error': 'Ошибка сервера. Не удалось создать QR-код.'})
    file = io.BytesIO()
    img.save(file, 'png')
    return True, file
