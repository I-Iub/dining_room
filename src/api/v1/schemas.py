import datetime
from typing import List

from pydantic import BaseModel


class UserIn(BaseModel):
    name: str


class UserOut(UserIn):
    uuid: str
