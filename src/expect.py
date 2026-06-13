from abc import ABC, abstractmethod
from typing import Callable


class Expect(ABC):
    def __init__(self, options: list[list[int]]):
        super().__init__()
        self.options = options
        self.tokens: list[int] = []

    def valid_tokens(self) -> set:
        result = set()

        if not self.tokens:
            return {x[0] for x in self.options}
        for option in [x for x in self.options
                       if len(x) > len(self.tokens)]:
            for option_token, token in zip(option, self.tokens):
                if option_token != token:
                    break
            else:
                result.add(option[len(self.tokens)])

        return result

    @abstractmethod
    def next_state(self, encoder: Callable) -> "Expect":
        raise NotImplementedError()


class ExpectParamDict(Expect):
    def next_state(self, encoder: Callable):
        return ExpectFunction([encoder('hoi')])


class ExpectKVSep(Expect):
    def collapse(self, token):
        pass


class ExpectFunction(Expect):
    def next_state(self, encoder: Callable) -> ExpectParamDict:
        # ","parameters":{"
        return ExpectParamDict([[2198, 13786, 22317]])


# EXAMPLE

# {"prompt":"What is the sum of 265 and 345?","name":"fn_add_numbers
# ","parameters":{"a":"265","b":"345"}}

# STRINGS TO TOKENS:

# ","parameters":{"
# [2198, 13786, 22317]

# ":"
# [3252]

# ","
# [2198]

# "}}\n
# [95642]
