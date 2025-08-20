from typing import Optional

from datetime import datetime, date
from sqlmodel import SQLModel, Field

from app.persistance.db import engine


class Person(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    phone: str
    tags: Optional[str] = None
    birthday: Optional[date] = None
    city: Optional[str] = None
    notes: Optional[str] = None


class Interaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    person_id: int = Field(foreign_key="person.id")
    date: datetime
    channel: str
    type: str
    summary: Optional[str] = None
    sentiment: Optional[float] = None


class Reminder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    person_id: int = Field(foreign_key="person.id")
    due_date: datetime
    reason: str
    status: str = Field(default="open")


# Garantir que as tabelas sejam criadas quando este módulo for importado
SQLModel.metadata.create_all(engine)
