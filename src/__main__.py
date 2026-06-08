from pathlib import Path
import argparse
import json
import time
import sys

# import numpy as np
from llm_sdk.llm_sdk import Small_LLM_Model


X = "\033[0m"
H = "\033[1m"
U = "\033[4m"


# Parsing arguments
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    prog='uv run -m src',
    description='Generating JSON using small large language models',
    epilog='Made by ekramer')

parser.add_argument('--functions_definition')
parser.add_argument('--input')
parser.add_argument('--output')

args = parser.parse_args()
try:
    defs = Path(args.functions_definition).read_text()
    tests = Path(args.input).read_text()
    example = Path('data/example.json').read_text()
    path_output = Path(args.output)
except Exception:
    parser.print_help()
    sys.exit(1)


# -----------------------------------------------------------------------------
model = Small_LLM_Model()

# prompt = "What is the sum of 40 and 2?"
# prompt = "Greet shrek"
prompt = "Reverse the string 'hello'"
# prompt = "What is the square root of 16?"
# prompt = "Replace all numbers in \"Hello 34 I'm 233 years old\" with NUMBERS"
context = f"""
Generate a JSON object that represents a function call from a prompt.
The prompt should not be solved, only the parameters and
function name need to be given to be used to solve it.

The JSON object contains exactly three keys:
- Prompt: Exact prompt used to create the object.
- Name: Name of the function called to solve the question.
- Parameters: Dictionary of the parameters' names and values.

Example output format:
{example}

Available functions:
{defs}

Prompt: "{prompt}"
JSON output: """

print(f"{H}Prompt:{X} {prompt}")
time_start = time.perf_counter()

context = model.encode(context)[0].tolist()
output = model.encode(f'{{"prompt": "{prompt}", "name": "')[0].tolist()
print(f"{H + U}Response{X}\n{model.decode(output)}", end='')
for _ in range(20):
    logits = model.get_logits_from_input_ids(context + output)
    output += [logits.index(max(logits))]
    print(model.decode([output[-1]]), end='', flush=True)

decoded = model.decode(output).strip()
path_output.parent.mkdir(exist_ok=True)
path_output.write_text(decoded)

vocab: dict = json.loads(Path(model.get_path_to_vocab_file()).read_text())
# with open("data/output/vocab.json", 'w') as f:
#     json.dump(vocab, f, indent='\t')

token_breakdown = [(x, list(vocab.keys())[x]) for x in output]
print(f"{H + U}\nTokens{X}")
for token in token_breakdown:
    print(f"{token[0]:>8} | {token[1]}")

print(
    "\nResponse finished in",
    round(time.perf_counter() - time_start),
    "seconds.")
