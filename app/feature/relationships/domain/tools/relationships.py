from typing import Literal, Optional

from pydantic import BaseModel
from sqlmodel import Session, select

from app.domain.tools.base import Tool, ToolResult

from app.feature.relationships.persistence.db import engine
from app.feature.relationships.persistence.models import Person, Interaction, Reminder

# === Add tools ===

class AddPerson(BaseModel):
    first_name: str
    last_name: str
    phone: str
    tags: Optional[str] = None
    birthday: Optional[str] = None
    city: Optional[str] = None
    notes: Optional[str] = None

def add_person_function(**data) -> str:
    with Session(engine) as session:
        person = Person.model_validate(data)
        session.add(person)
        session.commit()
        session.refresh(person)
        return f"Added person {person.first_name} {person.last_name} (id={person.id})"

add_person_tool = Tool(
    name="add_person",
    model=AddPerson,
    function=add_person_function,
)

class LogInteraction(BaseModel):
    person_id: int
    date: str
    channel: str
    type: str
    summary: Optional[str] = None
    sentiment: Optional[float] = None

def log_interaction_function(**data) -> str:
    with Session(engine) as session:
        interaction = Interaction.model_validate(data)
        session.add(interaction)
        session.commit()
        session.refresh(interaction)
        return f"Logged interaction id={interaction.id} for person_id={interaction.person_id}"

log_interaction_tool = Tool(
    name="log_interaction",
    model=LogInteraction,
    function=log_interaction_function,
)

class ScheduleReminder(BaseModel):
    person_id: int
    due_date: str
    reason: str
    status: Optional[str] = "open"

def schedule_reminder_function(**data) -> str:
    with Session(engine) as session:
        reminder = Reminder.model_validate(data)
        session.add(reminder)
        session.commit()
        session.refresh(reminder)
        return f"Scheduled reminder id={reminder.id} for person_id={reminder.person_id}"

schedule_reminder_tool = Tool(
    name="schedule_reminder",
    model=ScheduleReminder,
    function=schedule_reminder_function,
)

# === Query tools ===

class QueryPeople(BaseModel):
    name_contains: Optional[str] = None
    tag_contains: Optional[str] = None

def query_people_function(**kwargs) -> ToolResult:
    name_contains = kwargs.get("name_contains")
    tag_contains = kwargs.get("tag_contains")
    with Session(engine) as session:
        statement = select(Person)
        if name_contains:
            statement = statement.where((Person.first_name.contains(name_contains)) | (Person.last_name.contains(name_contains)))
        if tag_contains:
            statement = statement.where(Person.tags.contains(tag_contains))
        result = session.exec(statement).all()
        return ToolResult(content=str([repr(r) for r in result]), success=True)

query_people_tool = Tool(
    name="query_people",
    model=QueryPeople,
    function=query_people_function,
)

class QueryInteractions(BaseModel):
    person_id: Optional[int] = None
    channel: Optional[str] = None
    type: Optional[str] = None

def query_interactions_function(**kwargs) -> ToolResult:
    with Session(engine) as session:
        statement = select(Interaction)
        if kwargs.get("person_id") is not None:
            statement = statement.where(Interaction.person_id == kwargs["person_id"])
        if kwargs.get("channel"):
            statement = statement.where(Interaction.channel == kwargs["channel"])
        if kwargs.get("type"):
            statement = statement.where(Interaction.type == kwargs["type"])
        result = session.exec(statement).all()
        return ToolResult(content=str([repr(r) for r in result]), success=True)

query_interactions_tool = Tool(
    name="query_interactions",
    model=QueryInteractions,
    function=query_interactions_function,
)

class UpcomingReminders(BaseModel):
    days_ahead: int = 7

def upcoming_reminders_function(**kwargs) -> ToolResult:
    from datetime import datetime, timedelta
    horizon = datetime.utcnow() + timedelta(days=kwargs.get("days_ahead", 7))
    with Session(engine) as session:
        statement = select(Reminder).where(Reminder.due_date <= horizon, Reminder.status == "open")
        result = session.exec(statement).all()
        return ToolResult(content=str([repr(r) for r in result]), success=True)

upcoming_reminders_tool = Tool(
    name="upcoming_reminders",
    model=UpcomingReminders,
    function=upcoming_reminders_function,
)
