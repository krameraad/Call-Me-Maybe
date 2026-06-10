from abc import ABC, abstractmethod


class Expect(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def valid_tokens(self, tokens: list[int]) -> set:
        raise NotImplementedError()


class ExpectParameter(Expect):
    def collapse(self, token):
        pass


class ExpectFunction(Expect):
    def __init__(self, functions: list[list[int]]):
        super().__init__()
        self.functions = functions
        self.tokens: list[int] = []

    def valid_tokens(self) -> set:
        result = set()

        if not self.tokens:
            return {x[0] for x in self.functions}
        for function in [x for x in self.functions
                         if len(x) > len(self.tokens)]:
            for function_token, token in zip(function, self.tokens):
                if function_token != token:
                    break
            else:
                result.add(function[len(self.tokens)])

        return result
