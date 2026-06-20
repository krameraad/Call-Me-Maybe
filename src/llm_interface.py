import time
import json
from pathlib import Path
from typing import Any

from llm_sdk.llm_sdk import Small_LLM_Model

from .expect import Expect, ExpectFunction
from .formatting import X, H, U, C, D
from .models import FunctionDefinition, FunctionCall


class LLMInterface:
    """Interface class to assist in interacting with an LLM.
    `defs` is the functions defined for the LLM to use."""
    def __init__(self, defs: list[FunctionDefinition]):
        self.model = Small_LLM_Model()
        "Model interface provided by LLM SDK."

        self.vocab: list[str] = list(
            json.loads(
                Path(self.model.get_path_to_vocab_file()).read_text()
            ).keys()
        )
        "List of all tokens the model has in its vocabulary."

        self.context = self.get_tokens(f"""Available functions:
{'\n'.join([': '.join([x.name, x.description]) for x in defs])}""")
        "General context used to improve results for all prompts."
        print(f"{H + U + C}Context{X}\n{self.model.decode(self.context)}")
        self.state_context: dict[tuple[int, ...], list[tuple[int, ...]]] = {
            tuple(self.get_tokens(x.name)): [
                tuple(self.get_tokens(y)) for y in x.parameters.keys()
            ]
            for x in defs
        }
        "Dictionary of functions and their parameters, encoded as int tuples."

        type_factories = {
            "number": float,
            "integer": int,
            "boolean": lambda x: x.lower() in {'true', '1', 'yes'}
        }
        self.defs: dict[str, dict[str, Any]] = {x.name: {} for x in defs}
        "Functions and their corresponding parameters, along with their types."
        for i, params in enumerate(self.defs.values()):
            for parameter, content in defs[i].parameters.items():
                params.update(
                    {parameter: type_factories.get(content['type'], str)})

    def _add_token(
            self,
            output: list[int],
            state_tokens: list[int],
            tokens: list[int],
            autocomplete: bool = False
            ) -> bool:
        """Utility function for adding tokens to output.

        Parameters
        ----------
        output : list[int]
            Output list to add tokens to.
        state_tokens : list[int]
            State's tokens to also add tokens to.
        tokens : list[int]
            List of tokens to add.
        autocomplete : bool, optional
            Whether the token added was as a result of autocompletion,
            by default `False`

        Returns
        -------
        bool
            `True` if the token was truncated to preserve JSON format.
        """
        def _valid_len(s: str) -> int:
            "Get the length up to where a string is considered valid JSON."
            for i in range(1, len(s) + 1):
                try:
                    json.loads(f'["{s[:i]}"]')
                except json.JSONDecodeError:
                    try:
                        json.loads(f'["{s[:i + 1]}"]')
                        continue
                    except (json.JSONDecodeError, IndexError):
                        return i - 1
            return i

        s = self.model.decode(tokens)
        truncated_s = s

        if autocomplete:
            print(f"{D + s + X}", end='', flush=True)
        else:
            truncated_s = s[:_valid_len(s)]
            tokens = self.get_tokens(truncated_s)
            print(truncated_s, end='', flush=True)

        state_tokens.extend(tokens)
        output.extend(tokens)
        return s != truncated_s

    def get_tokens(self, s: str) -> list[int]:
        "Return the tokens received from encoding `s` as a list of integers."
        return self.model.encode(s)[0].tolist()

    def inspect(self, s: str) -> None:
        "Neatly print the tokens making up `s`."
        print(f"""{D + "─" * 9}┬{"─" * 30 + X}
{H}Token{X}    {D}│{X} {H}String{X}
{D + "─" * 9}┼{"─" * 30 + X}""")
        for token in self.get_tokens(s):
            print(f"{token:>8} {D}│{X} {self.vocab[token]}")
        print(f"{D + "─" * 9}┴{"─" * 30 + X}")

    def dump(self, obj: str, path: Path) -> None:
        """Dump a JSON string into a file according to a specification.
        Appends the object to a JSON array if one is present in the file.
        All parameters are converted to the correct types.

        Parameters
        ----------
        obj : str
            Object to load as JSON. This is the output of the LLM,
            and represents a single function call.
        path : Path
            Where to dump the JSON object.

        Raises
        ------
        JSONDecodeError
            `obj` is not in a valid function call format.
        OSError:
            Something goes wrong during file handling.
        """
        new_call = FunctionCall(**json.loads(obj))
        converted_params = {
            k: self.defs[new_call.name][k](v)
            for k, v in new_call.parameters.items()
        }
        function_calls = [{
            "prompt": new_call.prompt,
            "name": new_call.name,
            "parameters": converted_params
        }]
        path.parent.mkdir(exist_ok=True)
        try:
            function_calls = json.loads(path.read_text()) + function_calls
        except (json.JSONDecodeError, OSError, TypeError):
            pass
        with path.open('w') as f:
            json.dump(function_calls, f, indent='\t')

    def process_prompt(self, prompt: str, timeout: float = 30.0) -> str:
        """Generate a string representing a function call, based on a prompt.

        Parameters
        ----------
        prompt : str
            Prompt to base the function call on.
        timeout : float, optional
            When to prematurely terminate the response, in seconds,
            by default `30.0`

        Returns
        -------
        str
            Function call object as a string.

        Raises
        ------
        RuntimeError
            Time limit was reached.
        """
        print(f"{H + U + C}\nPrompt{X}\n{prompt}")
        time_start = time.perf_counter()

        context = self.context + self.get_tokens(
            f'\nPrompt: "{prompt}"\nJSON output: ')
        output = self.get_tokens(f'{{"prompt":"{prompt}","name":"')
        state: Expect | None = ExpectFunction(self.state_context)

        print(f"{H + U + C}Response{X}\n"
              f"{D + self.model.decode(output) + X}", end='')
        while time.perf_counter() - time_start < timeout:
            if state is None:
                break
            if not (allowed := state.get_allowed()):
                state = state.next_state()
                continue
            if len(allowed) == 1:
                next_tokens = [allowed.pop()]
                self._add_token(output, state.tokens, next_tokens, True)
                continue

            logits = self.model.get_logits_from_input_ids(context + output)
            if -1 not in allowed:
                for i in range(len(logits)):
                    if i not in allowed:
                        logits[i] = float('-inf')

            next_tokens = [logits.index(max(logits))]
            if self._add_token(output, state.tokens, next_tokens):
                state = state.next_state()
        else:
            raise RuntimeError(f"Time limit ({timeout}) reached.")

        print(
            f"\n{H}Response finished in "
            f"{round(time.perf_counter() - time_start)} seconds.{X}")

        return self.model.decode(output)
