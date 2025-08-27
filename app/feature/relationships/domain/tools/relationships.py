from typing import Callable, Optional, Type
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.domain.tools.tool import Tool, ToolResult
from app.feature.relationships.persistence.db import *
from app.feature.relationships.persistence.models import Person, Interaction, Reminder

# === Add tools ===

class AddPerson(BaseModel):
    first_name: str = Field(description="Primeiro nome da pessoa")
    last_name: str = Field(description="Sobrenome da pessoa")
    phone: str = Field(description="Número de telefone")
    tags: Optional[str] = Field(default=None, description="Tags para categorização")
    birthday: Optional[str] = Field(default=None, description="Data de aniversário")
    city: Optional[str] = Field(default=None, description="Cidade")
    notes: Optional[str] = Field(default=None, description="Notas adicionais")

class AddPersonTool(Tool):
    name: str = "add_person"
    description: str = "Add a new person to your contacts database"
    args_schema: Type[BaseModel] = AddPerson
    model: Type[BaseModel] = AddPerson
    
    def _run(self, **data) -> ToolResult:
        return super()._run(**data)
    
    async def _arun(self, **data) -> ToolResult:
        return self._run(**data)
    
    def execute(self, **data) -> ToolResult:
        with Session(engine) as session:
            person = Person.model_validate(data)
            session.add(person)
            session.commit()
            session.refresh(person)
            return ToolResult(content=f"Added person {person.first_name} {person.last_name} (id={person.id})", success=True)


class LogInteraction(BaseModel):
    person_id: int = Field(description="ID da pessoa para registrar a interação")
    date: str = Field(description="Data da interação")
    channel: str = Field(description="Canal de comunicação (ex: phone, email, in-person)")
    type: str = Field(description="Tipo de interação (ex: call, meeting, message)")
    summary: Optional[str] = Field(default=None, description="Resumo da interação")
    sentiment: Optional[float] = Field(default=None, description="Sentimento da interação (-1 a 1)")

class LogInteractionTool(Tool):
    name: str = "log_interaction"
    description: str = "Log an interaction with a person in your contacts"
    args_schema: Type[BaseModel] = LogInteraction
    model: Type[BaseModel] = LogInteraction
    
    def _run(self, **data) -> ToolResult:
        return super()._run(**data)
    
    async def _arun(self, **data) -> ToolResult:
        return self._run(**data)
    
    def execute(self, **data) -> ToolResult:
        with Session(engine) as session:
            interaction = Interaction.model_validate(data)
            session.add(interaction)
            session.commit()
            session.refresh(interaction)
            return ToolResult(content=f"Logged interaction id={interaction.id} for person_id={interaction.person_id}", success=True)        

class ScheduleReminder(BaseModel):
    person_id: int = Field(description="ID da pessoa para agendar o lembrete")
    due_date: str = Field(description="Data de vencimento do lembrete")
    reason: str = Field(description="Motivo do lembrete")
    status: Optional[str] = Field(default="open", description="Status do lembrete")

class ScheduleReminderTool(Tool):
    name: str = "schedule_reminder"
    description: str = "Schedule a reminder for a person"
    args_schema: Type[BaseModel] = ScheduleReminder
    model: Type[BaseModel] = ScheduleReminder
    function: Callable = None
    parse_model: bool = True 
    
    def _run(self, **data) -> ToolResult:
        return super()._run(**data)
    
    async def _arun(self, **data) -> ToolResult:
        return self._run(**data)

    def execute(self, **data) -> ToolResult:
        with Session(engine) as session:
            reminder = Reminder.model_validate(data)
            session.add(reminder)
            session.commit()
            session.refresh(reminder)
            return ToolResult(content=f"Scheduled reminder id={reminder.id} for person_id={reminder.person_id}", success=True)

# === Query tools ===

class QueryPeople(BaseModel):
    name_contains: Optional[str] = Field(default=None, description="Buscar por nome (primeiro ou último)")
    tag_contains: Optional[str] = Field(default=None, description="Buscar por tags")

class QueryPeopleTool(Tool):
    name: str = "query_people"
    description: str = "Search for people in your contacts. You can search by name (first or last name) or by tags. Both parameters are optional - if neither is provided, all contacts will be returned."
    args_schema: Type[BaseModel] = QueryPeople
    model: Type[BaseModel] = QueryPeople
    
    def _run(self, **kwargs) -> ToolResult:
        return super()._run(**kwargs)
    
    async def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)
    
    def execute(self, **kwargs) -> ToolResult:
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

class QueryInteractions(BaseModel):
    person_id: Optional[int] = Field(default=None, description="ID da pessoa para filtrar")
    channel: Optional[str] = Field(default=None, description="Canal de comunicação para filtrar")
    type: Optional[str] = Field(default=None, description="Tipo de interação para filtrar")

class QueryInteractionsTool(Tool):
    name: str = "query_interactions"
    description: str = "Search for interaction history with optional filters"
    args_schema: Type[BaseModel] = QueryInteractions
    model: Type[BaseModel] = QueryInteractions
    
    def _run(self, **kwargs) -> ToolResult:
        return super()._run(**kwargs)
    
    async def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)
    
    def execute(self, **kwargs) -> ToolResult:
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

class UpcomingReminders(BaseModel):
    days_ahead: int = Field(default=7, description="Número de dias à frente para buscar lembretes")

class UpcomingRemindersTool(Tool):
    name: str = "upcoming_reminders"
    description: str = "Get reminders due in the next specified number of days (default: 7 days)"
    args_schema: Type[BaseModel] = UpcomingReminders
    model: Type[BaseModel] = UpcomingReminders
    
    def _run(self, **kwargs) -> ToolResult:
        return super()._run(**kwargs)
    
    async def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)
    
    def execute(self, **kwargs) -> ToolResult:
        from datetime import datetime, timedelta
        horizon = datetime.utcnow() + timedelta(days=kwargs.get("days_ahead", 7))
        with Session(engine) as session:
            statement = select(Reminder).where(Reminder.due_date <= horizon, Reminder.status == "open")
            result = session.exec(statement).all()
            return ToolResult(content=str([repr(r) for r in result]), success=True)

# === Instâncias das ferramentas ===
add_person_tool = AddPersonTool()
log_interaction_tool = LogInteractionTool()
schedule_reminder_tool = ScheduleReminderTool()
query_people_tool = QueryPeopleTool()
query_interactions_tool = QueryInteractionsTool()
upcoming_reminders_tool = UpcomingRemindersTool()
