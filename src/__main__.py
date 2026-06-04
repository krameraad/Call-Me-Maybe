from pathlib import Path
import argparse
import json
import time

from llm_sdk.llm_sdk import Small_LLM_Model


X = "\033[0m"
H = "\033[1m"
I = "\033[3m"
U = "\033[4m"


parser = argparse.ArgumentParser(
            prog='uv run -m src',
            description='Generating JSON using small large language models',
            epilog='Made by ekramer')

parser.add_argument('--functions_definition')
parser.add_argument('--input')
parser.add_argument('--output')

args = parser.parse_args()
for arg in args:
    print(arg)
defs = Path(args.functions_definition).read_text()
tests = Path(args.input).read_text()
path_output = Path(args.output)

# model = Small_LLM_Model()

# vocab: dict = json.loads(Path(model.get_path_to_vocab_file()).read_text())

# prompt = "The sum of 2 and 3 is "
# print(f"{H + U}Prompt{X}\n{prompt}")
# time_start = time.perf_counter()

# context: list[int] = model.encode(prompt)[0].tolist()
# output: list[int] = []
# for _ in range(25):
#     logits = model.get_logits_from_input_ids(context + output)
#     output += [logits.index(max(logits))]

# print(f"{H + U}Response{X}\n{model.decode(output).strip()}")

# print(
#     "\nResponse finished in",
#     round(time.perf_counter() - time_start),
#     "seconds.")
