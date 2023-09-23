from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import relationship

from src.db.database import Base

NAME_MAX_LENGTH = 250


class User(Base):
    __tablename__ = 'users'
    uuid = Column(Uuid, primary_key=True)
    name = Column(String(length=NAME_MAX_LENGTH), unique=False, index=True)
    ticket = relationship('Ticket', back_populates='user')


class Ticket(Base):
    __tablename__ = 'tickets'
    uuid = Column(Uuid, primary_key=True)
    created = Column(DateTime)
    user_uuid = Column(Integer,
                       ForeignKey('users.uuid', ondelete='CASCADE'),
                       nullable=False, unique=True)
    user = relationship(User, back_populates='ticket')
    meals = relationship('Meal', back_populates='ticket')


class Meal(Base):
    __tablename__ = 'meals'
    id = Column(Integer, primary_key=True, index=True)
    ticket_uuid = Column(Integer,
                         ForeignKey('tickets.uuid'), nullable=False)
    ticket = relationship(Ticket, back_populates='meals')
    time = Column(DateTime)
