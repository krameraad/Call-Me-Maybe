from pydantic import BaseModel


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: dict[str, dict[str, str]]
    returns: dict[str, str]


class FunctionCall(BaseModel):
    prompt: str
    name: str
    parameters: dict[str, str | int | float | bool]
