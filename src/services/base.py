from uuid import uuid4

from sqlalchemy.sql.expression import insert

from src.models.users import User


async def create_user(name, session):
    user_uuid = uuid4()
    user = [dict(name=name, uuid=user_uuid)]
    statement = (
        insert(User).values(user)
    )
    await session.execute(statement)
    await session.commit()
    print(user_uuid)
    return {'name': name, 'uuid': user_uuid.hex}
