"Collection of states used for the LLM."

from abc import ABC, abstractmethod
from typing import Any


class Expect(ABC):
    'Base class for states assisting constrained decoding.'
    def __init__(self, context: Any):
        super().__init__()
        self.context = context
        self.tokens: list[int] = []

    def _valid_tokens(self, options: tuple[tuple[int, ...]]) -> set[int]:
        "Return set of tokens that are available for LLM to use."
        result: set[int] = set()

        if not self.tokens:
            return {x[0] for x in options}
        for option in [x for x in options
                       if len(x) > len(self.tokens)]:
            for option_token, token in zip(option, self.tokens):
                if option_token != token:
                    break
            else:
                result.add(option[len(self.tokens)])

        return result

    @abstractmethod
    def get_allowed(self) -> set[int]:
        'Access valid tokens from the state.'
        raise NotImplementedError()

    @abstractmethod
    def next_state(self) -> "Expect | None":
        'Return the next state.'
        raise NotImplementedError()


class ExpectEnd(Expect):
    'Final token of the LLM response: `"}}\\n`'
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(((95642,),))

    def next_state(self) -> None:
        return None


class ExpectKVSep(Expect):
    'Separates keys from values: `":"`'
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(((3252,),))

    def next_state(self) -> Expect:
        return ExpectValue(self.context)


class ExpectKey(Expect):
    'Every function has some parameters; these are the parameter names.'
    def get_allowed(self) -> set[int]:
        return self._valid_tokens((self.context[0],))

    def next_state(self) -> Expect:
        return ExpectKVSep(self.context[1:])


class ExpectSep(Expect):
    'Separates key/value pairs from each other: `","`'
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(((2198,),))

    def next_state(self) -> Expect:
        return ExpectKey(self.context)


class ExpectValue(Expect):
    "Values for parameters can be anything, as long as they're valid JSON."
    def get_allowed(self) -> set[int]:
        return {-1, -2}  # Special set to make every token valid.

    def next_state(self) -> Expect:
        if not self.context:
            return ExpectEnd(self.context)
        return ExpectSep(self.context)


class ExpectParameters(Expect):
    'Insert a segment that leads into the parameters: `","parameters":{"`'
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(((2198, 13786, 22317),))

    def next_state(self) -> Expect:
        return ExpectKey(self.context)


class ExpectFunction(Expect):
    'Select a function name.'
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(tuple(self.context.keys()))

    def next_state(self) -> Expect:
        return ExpectParameters(self.context.get(tuple(self.tokens)))
