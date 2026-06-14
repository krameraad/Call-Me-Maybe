from abc import ABC, abstractmethod


StateContext = dict[tuple[int], list[tuple[int]]] | list[tuple[int]]


class Expect(ABC):
    def __init__(self, context: StateContext):
        super().__init__()
        self.context = context
        self.tokens: list[int] = []

    def valid_tokens(self, options: tuple[tuple[int]]) -> set:
        result = set()

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
    def get_allowed(self) -> set:
        raise NotImplementedError()

    @abstractmethod
    def next_state(self) -> "Expect":
        raise NotImplementedError()


class ExpectEnd(Expect):
    def get_allowed(self) -> set:  # "}}\n
        return self.valid_tokens(((95642,),))

    def next_state(self) -> None:
        return None


class ExpectKVSep(Expect):
    def get_allowed(self) -> set:  # ":"
        return self.valid_tokens(((3252,),))

    def next_state(self) -> "ExpectValue":
        return ExpectValue(self.context)


class ExpectKey(Expect):
    def get_allowed(self) -> set:  # a / b
        return self.valid_tokens((self.context[0],))

    def next_state(self) -> ExpectKVSep:
        return ExpectKVSep(self.context[1:])


class ExpectSep(Expect):
    def get_allowed(self) -> set:  # ","
        return self.valid_tokens(((2198,),))

    def next_state(self) -> ExpectKey:
        return ExpectKey(self.context)


class ExpectValue(Expect):
    def get_allowed(self) -> set:  # 2 / 3
        if len(self.tokens) <= 3:
            return self.valid_tokens(((16, 16), (16, 17), (17, 16), (17, 17)))
        return set()

    def next_state(self) -> ExpectEnd | ExpectSep:
        if not self.context:
            return ExpectEnd(self.context)
        return ExpectSep(self.context)


class ExpectParameters(Expect):
    def get_allowed(self) -> set:  # ","parameters":{"
        return self.valid_tokens(((2198, 13786, 22317),))

    def next_state(self) -> ExpectKey:
        return ExpectKey(self.context)


class ExpectFunction(Expect):
    def get_allowed(self) -> set:  # fn_add_numbers
        return self.valid_tokens(tuple(self.context.keys()))

    def next_state(self) -> ExpectParameters:
        return ExpectParameters(self.context.get(tuple(self.tokens)))


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
