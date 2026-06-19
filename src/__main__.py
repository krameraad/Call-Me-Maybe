import argparse
import json
import time
import sys
from pathlib import Path

from .formatting import X, H, R
from .function_definition import FunctionDefinition


# Parse arguments.
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    prog='call_me_maybe',
    usage='uv run -m src '
          '[-h] [--functions_definition FUNCTIONS_DEFINITION] '
          '[--input INPUT] [--output OUTPUT] [-id]',
    description='Generating JSON using small large language models',
    epilog='Made by ekramer')

parser.add_argument(
    '--functions_definition',
    help='JSON file with definitions for functions to be called')
parser.add_argument(
    '--input',
    help='JSON file to read prompts from')
parser.add_argument(
    '--output',
    help='file to dump generated JSON objects in')
parser.add_argument(
    '-i', '--inspect',
    action='store_true',
    help='print token information for prompt results')
parser.add_argument(
    '-d', '--dump',
    action='store_true',
    help='dump vocabulary of the model')

args = parser.parse_args()
try:
    defs: list[FunctionDefinition] = json.loads(
        Path(args.functions_definition).read_text())
    tests: list[dict[str, str]] = json.loads(
        Path(args.input).read_text())
    path_output = Path(args.output)
except Exception:
    parser.print_help()
    sys.exit(1)


# Run prompts through LLM.
# -----------------------------------------------------------------------------
# Import llm_interface later because it's huge;
# we don't need to import all this just to print a help message
from .llm_interface import LLMInterface  # noqa: E402


interface = LLMInterface(defs)
if args.dump:
    try:
        with (path_output.parent / 'vocab.txt').open('w') as f:
            for i, token in enumerate(interface.vocab):
                f.write(f'{i:>8} {token}\n')
        print(f"{H}Successfully dumped model vocabulary.{X}\n")
    except OSError as e:
        print(H + R + f'Error while dumping vocabulary: {e}' + X,
              file=sys.stderr)

time_start = time.perf_counter()
for test in tests:
    try:
        obj = interface.process_prompt(test["prompt"]
                                       .replace('\\', '\\\\')
                                       .replace('"', '\\"'))
        try:
            interface.dump(obj, path_output)
        except (json.JSONDecodeError, OSError) as e:
            print(H + R + f'\nError: {e}' + X, file=sys.stderr)
    except RuntimeError as e:
        print(H + R + f'\nError: {e}' + X, file=sys.stderr)
    except KeyboardInterrupt:
        sys.exit(1)
    if args.inspect:
        interface.inspect(obj)

    time_total = round(time.perf_counter() - time_start)
    minutes, seconds = time_total // 60, time_total % 60
    print(
        f"{H}Running time is {minutes} minutes and {seconds} seconds.{X}")
