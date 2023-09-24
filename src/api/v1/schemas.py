import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class UserIn(BaseModel):
    name: str


class UserUUID(BaseModel):
    uuid: UUID


class UserOut(UserIn, UserUUID):
    pass


class TicketUUID(BaseModel):
    uuid: UUID


class TicketOut(TicketUUID):
    created: datetime.datetime
    user_uuid: UUID
