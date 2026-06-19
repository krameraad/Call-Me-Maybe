from typing import TypedDict


class FunctionDefinition(TypedDict):
    name: str
    description: str
    parameters: dict[str, dict[str, str]]
    returns: dict[str, str]
