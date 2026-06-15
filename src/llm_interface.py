import time
import json
from pathlib import Path

from llm_sdk.llm_sdk import Small_LLM_Model

from .expect import ExpectFunction
from .formatting import X, H, U, C, D


class LLMInterface:
    """Interface class to assist in interacting with an LLM."""
    def __init__(self, defs: str):
        self.model = Small_LLM_Model()
        "Model interface provided by LLM SDK."

        self.vocab: list[str] = list(
            json.loads(
                Path(self.model.get_path_to_vocab_file()).read_text()
            ).keys()
        )
        "List of all tokens the model has in its vocabulary."

        defs_obj = json.loads(defs)
        self.context = self.get_tokens(f"""Available functions:
{'\n'.join([': '.join([x['name'], x['description']]) for x in defs_obj])}""")
        "General context used to improve results for all prompts."
        print(f"{H + U + C}Context{X}\n{self.model.decode(self.context)}")
        self.defs: dict[tuple[int], list[tuple[int]]] = {
            tuple(self.get_tokens(x["name"])): [
                tuple(self.get_tokens(y)) for y in x["parameters"].keys()
            ]
            for x in defs_obj
        }
        "Dictionary of functions and their parameters, encoded as int tuples."

    def _add_token(
            self,
            output: list[int],
            state_tokens: list[int],
            token: int,
            autocomplete: bool
            ) -> None:
        "Add tokens to the output and the state's memory."
        state_tokens.append(token)
        output.append(token)
        if autocomplete:
            print(f"{D + self.model.decode([token]) + X}", end='', flush=True)
        else:
            print(self.model.decode([token]), end='', flush=True)

    def get_tokens(self, s: str) -> list[int]:
        "Return the tokens received from encoding as a list of integers."
        return self.model.encode(s)[0].tolist()

    def inspect(self, s: str) -> None:
        "Neatly print the tokens making up a string."
        print(f"""{D + "─" * 9}┬{"─" * 30 + X}
{H}Token{X}    {D}│{X} {H}String{X}
{D + "─" * 9}┼{"─" * 30 + X}""")
        for token in self.get_tokens(s):
            print(f"{token:>8} {D}│{X} {self.vocab[token]}")
        print(f"{D + "─" * 9}┴{"─" * 30 + X}")

    @staticmethod
    def dump(obj: str, path: Path) -> None:
        """Dump `obj` as a JSON string into the file pointed to by `path`.
        Appends the object to a JSON array if one is present in the file."""
        function_calls = [json.loads(obj)]
        path.parent.mkdir(exist_ok=True)
        try:
            function_calls = json.loads(path.read_text()) + function_calls
        except (json.JSONDecodeError, TypeError):
            pass
        with path.open('w') as f:
            json.dump(function_calls, f, indent='\t')

    def process_prompt(self, prompt: str, timeout: float = 30.0) -> str:
        """Try to complete `prompt` within `timeout` seconds.
        Returns the result decoded to a string."""
        print(f"{H + U + C}\nPrompt{X}\n{prompt}")
        time_start = time.perf_counter()

        context = self.context + self.get_tokens(
            f'\nPrompt: "{prompt}"\nJSON output: ')
        output = self.get_tokens(f'{{"prompt":"{prompt}","name":"')
        state = ExpectFunction(self.defs)

        print(f"{H + U + C}Response{X}\n"
              f"{D + self.model.decode(output) + X}", end='')
        while time.perf_counter() - time_start < timeout:
            allowed = state.get_allowed()
            if not allowed:
                state = state.next_state()
                if not state:
                    break
                continue
            if len(allowed) == 1:
                next_token = allowed.pop()
                self._add_token(output, state.tokens, next_token, True)
                continue

            logits = self.model.get_logits_from_input_ids(context + output)
            if -1 not in allowed:
                for i in range(len(logits)):
                    if i not in allowed:
                        logits[i] = float('-inf')

            next_token = logits.index(max(logits))
            if state.early_exit(
                    self.model.decode(state.tokens + [next_token])):
                state = state.next_state()
                if not state:
                    break
                continue
            self._add_token(output, state.tokens, next_token, False)
        else:
            raise RuntimeError(f"Time limit ({timeout}) reached.")

        print(
            f"\n{H}Response finished in "
            f"{round(time.perf_counter() - time_start)} seconds.{X}")

        return self.model.decode(output)
