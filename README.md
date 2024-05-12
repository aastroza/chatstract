# chatstract

**Chatstract** is a tool that progressively extracts structured information from multi-turn user chats using pydantic schemas and LLMs. Powered by [Instructor](https://github.com/jxnl/instructor/).

## Basic Example

[Code](examples/simple_model.py)

First, create the pydantic model you wish to fill out through a conversational method.

```python
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional

class Task(BaseModel):
    title: str = Field(description="A short title of the task.")
    due_date: date = Field(description="The deadline for the task. Current year: 2024")
    responsable: str = Field(description="The person assigned to solve the task")
    location: str = Field(description="The location where the task will be performed")
    status: Optional[str] = Field(description="The status of the task", default=None)
```

Then, use Chatstract to populate the data model with values from sequential messages provided by the user.

```python
from chatstract.core import Chat

chat = Chat(data_model = Task)

messages = ["Jack has to clean his desk",
            "The deadline is september 7th",
            "This task is for the Downtown office",
            "I messed up, the task is for Dorothy at the Uptown office",
            "The status for this task is 'Done'",]

for message in messages:
    info = chat.chat_ai(message)
    print(f"User message: {message}")
    print(f"Data: {chat.data_values}")
    
    if len(info.answer) == 0:
        print("Missing information: None")
        print("Follow-up question: None")
        print("\n===\n")
        continue
    
    for question in info.answer:
        print(f"Missing information: {question.missing_information_key}")
        print(f"Follow-up question: {question.question}")

    print("\n===\n")
```

Below is the output you can expect:

```
User message: Jason has to clean his desk
Data: {'title': 'Clean the desk', 'due_date': None, 'responsable': 'Jason', 'location': None, 'status': None}
Missing information: due_date
Follow-up question: What is the due date for the task 'Clean the desk'?
Missing information: location
Follow-up question: Where should the task 'Clean the desk' be performed?

===

User message: The deadline is september 7th
Data: {'title': 'Clean the desk', 'due_date': datetime.date(2024, 9, 7), 'responsable': 'Jason', 'location': None, 'status': None}
Missing information: location
Follow-up question: What is the location for the task 'Clean the desk'?

===

User message: This task is for the Downtown office
Data: {'title': 'Clean the desk', 'due_date': datetime.date(2024, 9, 7), 'responsable': 'Jason', 'location': 'Downtown office', 'status': None}
Missing information: None
Follow-up question: None

===

User message: I messed up, the task is for Dorothy at the Uptown office
Data: {'title': 'Clean the desk', 'due_date': datetime.date(2024, 9, 7), 'responsable': 'Dorothy', 'location': 'Uptown office', 'status': None}
Missing information: None
Follow-up question: None

===

User message: The status for this task is 'Done'
Data: {'title': 'Clean the desk', 'due_date': datetime.date(2024, 9, 7), 'responsable': 'Dorothy', 'location': 'Uptown office', 'status': 'Done'}
Missing information: None
Follow-up question: None

===
```