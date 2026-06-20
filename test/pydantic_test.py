"Test pydantic models."

import sys
from pathlib import Path
import json

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


func = FunctionDefinition(
    name="fn_add",
    description="Add a number.",
    parameters={"x": {"type": "num"}},
    returns={"ret": "num"}
)
call = FunctionCall(
    prompt="Example prompt",
    name="fn_example",
    parameters={"x": 5},
)

Path('data/output').mkdir(exist_ok=True)
with open("data/output/pydantic_test.json", 'w') as f:
    json.dump(vars(call), f, indent='\t')

try:
    func = FunctionDefinition(
        name="fn_add",
        description="Add a number.",
        parameters={"x": {"type": 1}},  # type: ignore
        returns={"ret": "num"}
    )
except Exception as e:
    print(f'\033[1;91mError: {e}\033[0m',
          file=sys.stderr)
