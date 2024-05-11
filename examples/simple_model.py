from datetime import date
from pydantic import BaseModel, Field
from typing import Optional

from chatstract.core import Chat

class Task(BaseModel):
    description: Optional[str] = Field(description="A short description of the task.", default=None)
    due_date: Optional[date] = Field(description="The deadline for the task.", default=None)
    responsable: Optional[str] = Field(description="The person assigned to solve the task", default=None)

chat = Chat()
info = chat.chat_ai(message = "John Doe has to clean the office", data_model = Task)
print(info.missing_information)
print(info.question)