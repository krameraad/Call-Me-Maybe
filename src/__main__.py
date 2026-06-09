import argparse
import json
import time
import sys
from pathlib import Path

from .llm_interface import LLMInterface
from .formatting import X, H, R


# Parse arguments.
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    prog='call_me_maybe',
    usage='uv run -m src '
          '[-h] [--functions_definition FUNCTIONS_DEFINITION] '
          '[--input INPUT] [--output OUTPUT] [-i]',
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

args = parser.parse_args()
try:
    defs = Path(args.functions_definition).read_text()
    tests: list[dict[str, str]] = json.loads(Path(args.input).read_text())
    path_output = Path(args.output)
    inspect = bool(args.inspect)
except Exception:
    parser.print_help()
    sys.exit(1)


# Run prompts through LLM.
# -----------------------------------------------------------------------------
interface = LLMInterface(defs)
with open("data/output/vocab.json", 'w') as f:
    json.dump(interface.vocab, f)

time_start = time.perf_counter()
for test in tests:
    try:
        obj = interface.process_prompt(test["prompt"])
        interface.dump(obj, path_output)
    except RuntimeError as e:
        print('\n' + H + R + str(e) + X, file=sys.stderr)
    if inspect:
        interface.inspect(obj)

    time_total = round(time.perf_counter() - time_start)
    minutes, seconds = time_total // 60, time_total % 60
    print(
        f"{H}Running time is {minutes} minutes and {seconds} seconds.{X}")
