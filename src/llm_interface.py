import time
import json
from pathlib import Path

from llm_sdk.llm_sdk import Small_LLM_Model

from .expect import ExpectFunction
from .formatting import X, H, U, C, D


class LLMInterface:
    def __init__(self, defs: str):
        self.model = Small_LLM_Model()
        self.vocab = list(
            json.loads(
                Path(self.model.get_path_to_vocab_file()).read_text()
            ).keys()
        )
        self.context = self.get_tokens(f"""
Generate a JSON object that represents a function call from a prompt.
The prompt should not be solved, only the parameters and
function name need to be given to be used to solve it.

The JSON object contains exactly three keys:
- Prompt: Exact prompt used to create the object.
- Name: Name of the function called to solve the question.
- Parameters: Dictionary of the parameters' names and values.

Example output format:
{{"prompt": "What is the sum of 2 and 3?",\
"name": "fn_add_numbers",\
"parameters": {{"a": 2.0, "b": 3.0}}'

Available functions:
{defs}\n""")
        self.defs: dict[tuple[int], list[tuple[int]]] = {
            tuple(self.get_tokens(x["name"])): [
                tuple(self.get_tokens(y)) for y in x["parameters"].keys()
            ]
            for x in json.loads(defs)
        }

    def add_token(
            self,
            output: list[int],
            state_tokens: list[int],
            token: int,
            autocomplete: bool
            ) -> None:
        state_tokens.append(token)
        output.append(token)
        if autocomplete:
            print(f"{D + self.model.decode([token]) + X}", end='', flush=True)
        else:
            print(self.model.decode([token]), end='', flush=True)

    def get_tokens(self, s: str) -> list[int]:
        return self.model.encode(s)[0].tolist()

    def inspect(self, s: str) -> None:
        "Neatly print the tokens making up a string."
        print(f"{H + U}\nTokens{X}")
        for token in self.model.encode(s)[0].tolist():
            print(f"{token:>8} | {self.vocab[token]}")
        print()

    @staticmethod
    def dump(obj: str, path: Path) -> None:
        """Dump `obj` as a JSON string into the file pointed to by `path`.
        Appends the object to a JSON array if one is present in the file."""
        path.parent.mkdir(exist_ok=True)
        if path.exists():
            function_calls = json.loads(path.read_text())
            if not isinstance(function_calls, list):
                function_calls = []
        else:
            function_calls = []
        function_calls += [json.loads(obj)]
        with path.open('w') as f:
            json.dump(function_calls, f, indent='\t')

    def process_prompt(self, prompt: str, limit: int = 100) -> str:
        """Generate up to `limit` tokens, completing `prompt`.
        Returns the result decoded to a string."""
        print(f"{H + U + C}\nPrompt{X}\n{prompt}")
        time_start = time.perf_counter()

        context = self.context + self.get_tokens(
            f'Prompt: "{prompt}"\nJSON output: ')
        output = self.get_tokens(f'{{"prompt":"{prompt}","name":"')
        state = ExpectFunction(self.defs)

        print(f"{H + U + C}Response{X}\n"
              f"{D + self.model.decode(output) + X}", end='')
        for _ in range(limit):
            allowed = state.get_allowed()
            if not allowed:
                state = state.next_state()
                if not state:
                    break
                continue
            if len(allowed) == 1:
                next_token = allowed.pop()
                self.add_token(output, state.tokens, next_token, True)
                continue

            logits = self.model.get_logits_from_input_ids(context + output)
            if -1 not in allowed:
                for i in range(len(logits)):
                    if i not in allowed:
                        logits[i] = float('-inf')

            next_token = logits.index(max(logits))
            if next_token in state.exit_tokens():
                state.tokens.append(next_token)
                continue
            self.add_token(output, state.tokens, next_token, False)
        else:
            raise RuntimeError(f"Token limit ({limit}) reached.")

        print(
            f"\n{H}Response finished in "
            f"{round(time.perf_counter() - time_start)} seconds.{X}")

        return self.model.decode(output)
