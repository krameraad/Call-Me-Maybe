import argparse
import json
import time
import sys
from pathlib import Path

from pydantic import ValidationError

from .formatting import X, H, R
from .data_models import FunctionDefinition


# Parse arguments.
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    prog='call_me_maybe',
    usage='uv run -m src '
          '[-h] [-f FUNCTIONS_DEFINITION] '
          '[-i INPUT] [-o OUTPUT] [-d DUMP] [-e]',
    description='Generating JSON using small large language models',
    epilog='Made by ekramer')

parser.add_argument(
    '-f', '--functions_definition',
    help='JSON file with definitions for functions to be called')
parser.add_argument(
    '-i', '--input',
    help='JSON file to read prompts from')
parser.add_argument(
    '-o', '--output',
    help='file to dump generated JSON objects in')
parser.add_argument(
    '-m', '--model',
    help='LLM to download and use from Hugging Face')
parser.add_argument(
    '-d', '--dump',
    help='path to dump vocabulary of the model')
parser.add_argument(
    '-e', '--examine',
    action='store_true',
    help='print token information for prompt results')

args = parser.parse_args()
model = args.model if args.model else "Qwen/Qwen3-0.6B"
defs = []
try:
    if args.dump:
        try:
            path_dump = Path(args.dump)
        except (OSError, TypeError):
            raise OSError("Invalid dump path.")
    else:
        try:
            obj = json.loads(Path(args.functions_definition).read_text())
        except (OSError, TypeError):
            raise OSError("Invalid function definition path.")
        if not isinstance(obj, list):
            raise TypeError("Function definitions must be a JSON list.")
        defs = [FunctionDefinition(**x) for x in obj]

        try:
            obj = json.loads(Path(args.input).read_text())
        except (OSError, TypeError):
            raise OSError("Invalid input path.")
        if not isinstance(obj, list):
            raise TypeError("Tests must be a JSON list.")
        tests = [str(x["prompt"]) for x in obj]

        try:
            path_output = Path(args.output)
        except (OSError, TypeError):
            raise OSError("Invalid output path.")
except (OSError, TypeError) as e:
    print(H + R + f'Error while loading program: {e}' + X, file=sys.stderr)
    parser.print_help()
    sys.exit(1)


# Run prompts through LLM.
# -----------------------------------------------------------------------------
# Import llm_interface later because it's huge;
# we don't need to import all this just to print a help message
from .llm_interface import LLMInterface  # noqa: E402

try:
    interface = LLMInterface(model, defs)
except Exception as e:
    print(H + R + f'Error while initializing LLM: {e}' + X, file=sys.stderr)
    sys.exit(1)

if args.dump:
    try:
        with path_dump.open('w') as f:
            for i, token in enumerate(interface.vocab):
                f.write(f'{i:>16} {token}\n')
        print(f"{H}Successfully dumped model vocabulary.{X}\n")
        sys.exit(0)
    except OSError as e:
        print(H + R + f'Error while dumping vocabulary: {e}' + X,
              file=sys.stderr)
        sys.exit(1)

time_start = time.perf_counter()
for test in tests:
    try:
        obj = interface.process_prompt(
            test.replace('\\', '\\\\').replace('"', '\\"'))
        try:
            interface.dump(obj, path_output)
        except (json.JSONDecodeError, OSError, ValidationError) as e:
            print(H + R + f'\nError while dumping output: {e}' + X,
                  file=sys.stderr)
    except RuntimeError as e:
        obj = None
        print(H + R + f'\nError while processing prompt: {e}' + X,
              file=sys.stderr)
    except KeyboardInterrupt:
        sys.exit(1)
    if args.examine and obj is not None:
        interface.inspect(obj)

    time_total = round(time.perf_counter() - time_start)
    minutes, seconds = time_total // 60, time_total % 60
    print(
        f"{H}Running time is {minutes} minutes and {seconds} seconds.{X}")
