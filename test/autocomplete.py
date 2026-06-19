"Demonstrate autocompletion in a simple environment."


class Autocomplete:
    def __init__(self, functions: list[list[int]]):
        self.functions = functions
        self.tokens: list[int] = []

    def valid_tokens(self) -> set[int]:
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


ac = Autocomplete([[2, 8, 1], [4, 0, 1, 1], [2], [4, 0], [4, 0, 2, 1]])

while True:
    vt = ac.valid_tokens()
    if not vt:
        print("Sequence complete")
        break
    print("Valid tokens:", vt)
    n = int(input("Next token: "))
    if n in vt:
        ac.tokens.append(n)
    else:
        print("Invalid token")
