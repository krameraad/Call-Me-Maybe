from enum import Enum, auto


class OutputState(Enum):
    "State of the JSON output generation by an LLM."
    FUNC_NAME = auto()
    PARAM_START = auto()
    PARAM_END = auto()
