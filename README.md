# chatstract

**Chatstract** is a tool that progressively extracts structured information from multi-turn user chats using pydantic schemas and LLMs.

## Basic Example

[Code](examples/simple_model.py)

First, create the pydantic model you wish to fill out through a conversational method.

```python
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional

class Task(BaseModel):
    title: Optional[str] = Field(description="A short title of the task.", default=None)
    due_date: Optional[date] = Field(description="The deadline for the task. Current year: 2024", default=None)
    responsable: Optional[str] = Field(description="The person assigned to solve the task", default=None)
    location: Optional[str] = Field(description="The location where the task will be performed", default=None)
```

Then, use Chatstract to populate the data model with values from sequential messages provided by the user.

```python
from chatstract.core import Chat

chat = Chat()

messages = ["Jack has to clean his desk",
            "The deadline is september 7th",
            "This task is for the Downtown office",
            "I messed up, the task is for Dorothy at the Uptown office",]

for message in messages:
    info = chat.chat_ai(message = message, data_model = Task)
    print(f"User message: {message}")
    print(f"Data: {chat.data}")
    print(f"Missing information: {info.missing_information}")
    print(f"Follow-up question: {info.question}\n")
```

Below is the output you can expect:

```
User message: Jack has to clean his desk
Data: {'title': 'Clean the desk', 'due_date': None, 'responsable': 'Jack', 'location': None}
Missing information: ['due_date', 'location']
Follow-up question: Could you please provide the due date and location for the task 'Clean the desk'?

User message: The deadline is september 7th
Data: {'title': 'Clean the desk', 'due_date': datetime.date(2024, 9, 7), 'responsable': 'Jack', 'location': None}
Missing information: ['location']
Follow-up question: Could you please provide the location where the task 'Clean the desk' should be performed?

User message: This task is for the Downtown office
Data: {'title': 'Clean the desk', 'due_date': datetime.date(2024, 9, 7), 'responsable': 'Jack', 'location': 'Downtown office'}
Missing information: []
Follow-up question: None

User message: I messed up, the task is for Dorothy at the Uptown office
Data: {'title': 'Clean the desk', 'due_date': datetime.date(2024, 9, 7), 'responsable': 'Dorothy', 'location': 'Uptown office'}
Missing information: []
Follow-up question: None
```