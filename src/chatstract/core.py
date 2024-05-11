from pydantic import BaseModel, Field
from typing import Optional, List
import instructor
from openai import OpenAI

class Conversation(BaseModel):
    missing_information: List[str] = Field(description="List of missing information about the data.")
    question: Optional[str] = Field(description="A follow up question to ask the user about the missing information", default=None)

class Chat(BaseModel):
    """Handles chat interactions with an AI model to discuss missing data."""
    data: dict = Field(description="The data to be completed.", default=None)

    def chat_ai(self, message: str, data_model: BaseModel) -> Conversation:
        """Generates a conversation about missing data based on a user's message."""

        client = instructor.from_openai(OpenAI())

        if not self.data:
            self.data = client.chat.completions.create(
                model="gpt-4",
                temperature = 0,
                response_model=data_model,
                messages=[{"role": "user", "content": message}],
            )
        else:
            self.data = client.chat.completions.create(
                model="gpt-4",
                temperature = 0,
                response_model=data_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"{message}",
                    },
                    {"role": "user", "content": message},
                ],
            )

        return client.chat.completions.create(
            model="gpt-4",
            temperature = 0,
            response_model=Conversation,
            messages=[
                {
                    "role": "system",
                    "content": "You are a world class conversational algorithm to ask questions about missing data values. You are going to receive a python dict with some missing data values. Please ask the user for the missing information.",
                },
                {"role": "user", "content": f"{dict(self.data)}"},
            ]
        )