from pydantic import BaseModel, Field
from typing import Optional, List
import instructor
from openai import OpenAI

class Conversation(BaseModel):
    missing_information: List[str] = Field(description="List of keys from the dictionary where the associated values are None, indicating missing information.",
                                           default = [])
    question: Optional[str] = Field(description="A follow-up question to ask the user, aimed at gathering the missing information identified by the keys.",
                                    default=None)

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
            ).model_dump()
        else:
            new_data = client.chat.completions.create(
                model="gpt-4",
                temperature = 0,
                response_model=data_model,
                messages=[
                    {

                        "role": "system",
                        "content": """You are an iterative data completion assistant.
                                    You will receive a Python dictionary containing some existing data values and a user message that includes updates or new data.
                                    Please carefully analyze the user's message, extract relevant information, and update the dictionary accordingly.
                                    Ensure that the updated dictionary is accurate and reflects all new data provided by the user.""",
                    },
                    {"role": "user", "content": f"current dict: {self.data}"},
                    {"role": "user", "content": f"message: {message}"},
                ],
            ).model_dump()

            self.data = {key: (new_data[key] if new_data[key] is not None else self.data[key]) for key in self.data}

        return client.chat.completions.create(
            model="gpt-4",
            temperature = 0,
            response_model=Conversation,
            messages=[
                {
                    "role": "system",
                    "content": """You are a world class conversational algorithm to ask questions about missing data values.
                                You are going to receive a python dict with some missing data values.
                                Please ask the user for the missing information.""",
                },
                {"role": "user", "content": f"{self.data}"},
            ]
        )