from typing import TypedDict


class FunctionDefinitions(TypedDict):
    name: str
    description: str
    parameters: dict[str, dict[str, str]]
    returns: dict[str, str]
