from pydantic import BaseModel, Field, model_validator, ValidationInfo
from typing import Optional, List, Type
import instructor
from openai import OpenAI

from chatstract.utils import partial_model, list_mandatory

class Question(BaseModel):
    missing_information_key: str = Field(description="Key from the dictionary where the associated values is None, indicating missing information.",
                                           default = None)
    question: Optional[str] = Field(description="A follow-up question to ask the user, aimed at gathering the missing information identified by the key.",
                                    default=None)
    
    @model_validator(mode="after")
    def validate_missing_fields(self, info: ValidationInfo) -> "Question":
        mandatory_fields = info.context.get("mandatory_fields", [])
        if self.missing_information_key not in mandatory_fields:
            self.missing_information_key = None
        return self

class Conversation(BaseModel):
    answer: List[Question] = Field(description="List of questions to ask the user to gather missing information.",
                                           default = [])
    
    @model_validator(mode="after")
    def validate_questions(self) -> "Conversation":
        self.answer = [question for question in self.answer if question.missing_information_key is not None]
        return self

class Chat(BaseModel):
    """Handles chat interactions with an AI model to discuss missing data."""
    data_values: dict = Field(description="The data to be completed.", default=None)
    data_model: Type[BaseModel] = Field(description="The Pydantic model to be used for the data.", default=None)
    mandatory_fields: List[str] = Field(description="The mandatory fields of the data model.", default=[])

    def __init__(self, **data):
        super().__init__(**data)
        if self.data_model:
            self.mandatory_fields = list_mandatory(self.data_model)
            self.data_model = partial_model(self.data_model)

    def chat_ai(self, message: str) -> Conversation:
        """Generates a conversation about missing data based on a user's message."""

        client = instructor.from_openai(OpenAI())

        if not self.data_values:
            self.data_values = client.chat.completions.create(
                model="gpt-4",
                temperature = 0,
                response_model=self.data_model,
                messages=[{"role": "user", "content": message}],
            ).model_dump()
        else:
            new_data = client.chat.completions.create(
                model="gpt-4",
                temperature = 0,
                response_model=self.data_model,
                messages=[
                    {

                        "role": "system",
                        "content": """You are an iterative data completion assistant.
                                    You will receive a Python dictionary containing some existing data values and a user message that includes updates or new data.
                                    Please carefully analyze the user's message, extract relevant information, and update the dictionary accordingly.
                                    Ensure that the updated dictionary is accurate and reflects all new data provided by the user.""",
                    },
                    {"role": "user", "content": f"current dict: {self.data_values}"},
                    {"role": "user", "content": f"message: {message}"},
                ],
            ).model_dump()

            self.data_values = {key: (new_data[key] if new_data[key] is not None else self.data_values[key]) for key in self.data_values}

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
                {"role": "user", "content": f"{self.data_values}"},
            ],
            validation_context={"mandatory_fields": self.mandatory_fields},
        )