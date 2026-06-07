from pathlib import Path
import argparse
import json
import time
import sys

import numpy as np
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
    path_output = Path(args.output)
except Exception:
    parser.print_help()
    sys.exit(1)


# -----------------------------------------------------------------------------
model = Small_LLM_Model()

prompt = "What is the sum of 40 and 2?"
context = f"""
Generate a JSON object that represents a function call.
Available functions are:
{defs}

Now, {prompt}\nJSON output: """

print(f"{H + U}Prompt{X}\n{context}")
time_start = time.perf_counter()

context = model.encode(context)[0].tolist()
output = []
for _ in range(25):
    logits = model.get_logits_from_input_ids(context + output)
    output += [logits.index(max(logits))]

decoded = model.decode(output).strip()
print(f"{H + U}Response{X}\n{decoded}")
path_output.parent.mkdir(exist_ok=True)
path_output.write_text(decoded)

vocab: dict = json.loads(Path(model.get_path_to_vocab_file()).read_text())
with open("data/output/vocab.json", 'w') as f:
    json.dump(vocab, f, indent='\t')

print(
    "\nResponse finished in",
    round(time.perf_counter() - time_start),
    "seconds.")
