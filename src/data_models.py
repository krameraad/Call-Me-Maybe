from pathlib import Path
from argparse import Namespace

from pydantic import BaseModel


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: dict[str, dict[str, str]]
    returns: dict[str, str]


class StateContext(BaseModel):
    functions: dict[tuple[int, ...], list[tuple[int, ...]]]
    parameters: list[tuple[int, ...]] = []
    param_def: tuple[int, ...]  # ","parameters":{"
    kvsep: tuple[int, ...]  # ":"
    sep: tuple[int, ...]  # ","
    end: tuple[int, ...]  # "}}\n


class FunctionCall(BaseModel):
    prompt: str
    name: str
    parameters: dict[str, str | int | float | bool]


class Args(Namespace):
    functions_definition: list[FunctionDefinition]
    input: list[str]
    output: Path
    model: str
    dump: Path | None
    examine: bool
    timeout: float
