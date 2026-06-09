import time
import json
from pathlib import Path

from llm_sdk.llm_sdk import Small_LLM_Model

from .output_state import OutputState
from .formatting import X, H, U, R, C


class LLMInterface:
    def __init__(self, defs: str):
        self.model = Small_LLM_Model()
        self.vocab = list(
            json.loads(
                Path(self.model.get_path_to_vocab_file()).read_text()
            ).keys()
        )
        self.context = self.model.encode(f"""
Generate a JSON object that represents a function call from a prompt.
The prompt should not be solved, only the parameters and
function name need to be given to be used to solve it.

The JSON object contains exactly three keys:
- Prompt: Exact prompt used to create the object.
- Name: Name of the function called to solve the question.
- Parameters: Dictionary of the parameters' names and values.

Example output format:
{{"prompt": "What is the sum of 2 and 3?", \
"name": "fn_add_numbers", \
"parameters": {{"a": 2.0, "b": 3.0}}'

Available functions:
{defs}\n""")[0].tolist()

    def inspect(self, s: str) -> None:
        "Neatly print the tokens making up a string."
        print(f"{H + U}\nTokens{X}")
        for token in self.model.encode(s)[0].tolist():
            print(f"{token:>8} | {self.vocab[token]}")
        print()

    def dump(self, obj: str, path: Path) -> None:
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

    def process_prompt(self, prompt: str, limit: int = 50) -> str:
        """Generate up to `limit` tokens, completing `prompt`.
        Returns the result decoded to a string."""
        print(f"{H + U + C}\nPrompt{X}\n{prompt}")
        time_start = time.perf_counter()

        context = self.context + self.model.encode(
            f'Prompt: "{prompt}"\nJSON output: ')[0].tolist()
        output = self.model.encode(
            f'{{"prompt": "{prompt}", "name": "'
        )[0].tolist()
        state = OutputState.FUNC_NAME

        print(f"{H + U + C}Response{X}\n{self.model.decode(output)}", end='')
        for _ in range(limit):
            logits = self.model.get_logits_from_input_ids(context + output)
            next_token = logits.index(max(logits))
            output += [next_token]
            print(self.model.decode([next_token]), end='', flush=True)

            if next_token == 497 and state == OutputState.FUNC_NAME:
                state = OutputState.PARAM_START
                output += [330, 13786, 788, 5212]
                print(' "parameters": {"', end='', flush=True)
            if next_token == 788 and state == OutputState.PARAM_START:
                state = OutputState.PARAM_END
                output += [330]
                print(' "', end='', flush=True)
            if next_token == 497 and state == OutputState.PARAM_END:
                state = OutputState.PARAM_START
                output += [330]
                print(' "', end='', flush=True)

            if next_token == 95642:
                break
        else:
            print(f"\n{H + R}Token limit ({limit}) reached! Aborting.{X}")

        print(
            f"\n{H}Response finished in "
            f"{round(time.perf_counter() - time_start)} seconds.{X}")

        return self.model.decode(output)
