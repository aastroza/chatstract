from pydantic import BaseModel, Field
from typing import Optional, List
import instructor
from openai import OpenAI


class User(BaseModel):
    name: Optional[str] = Field(description="The name of the user.", default=None)
    age: Optional[int] = Field(description="The age of the user.", default=None)
    email: Optional[str] = Field(description="The email of the user.", default=None)

class Conversation(BaseModel):
    missing_information: List[str] = Field(description="List of missing information about the data.")
    question: Optional[str] = Field(description="A follow up question to ask the user about the missing information", default=None)
# Patch the OpenAI client
client = instructor.from_openai(OpenAI())


def chat_ai(message: str, data_model: BaseModel) -> Conversation:
    data = client.chat.completions.create(
        model="gpt-4",
        temperature = 0,
        response_model=data_model,
        messages=[{"role": "user", "content": message}],
    )

    return client.chat.completions.create(
        model="gpt-4",
        temperature = 0,
        response_model=Conversation,
        messages=[
            {
                "role": "system",
                "content": "You are a world class algorithm to ask questions about missing data values. You are going to receive a python dict with some missing data values. Please ask the user for the missing information.",
            },
            {"role": "user", "content": f"{dict(data)}"},
        ]
    )


# info = chat_ai(message = "John Doe is a man", data_model = User)
# print(info.missing_information)
# print(info.question)

class Task(BaseModel):
    description: Optional[str] = Field(description="The description of the task.", default=None)
    due_date: Optional[str] = Field(description="The deadline for the task.", default=None)
    responsable: Optional[str] = Field(description="The person assigned to solve the task", default=None)


info = chat_ai(message = "John Doe has to clean the office", data_model = Task)
print(info.missing_information)
print(info.question)