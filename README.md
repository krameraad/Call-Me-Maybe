*This project has been created as part of the 42 curriculum by ekramer*

# Call-Me-Maybe
In this project, we use a small large language model
to generate JSON objects that represent *function calls*.
The output must maintain 100% correct JSON format,
which is not reliable for simple LLMs.
This is where **constrained decoding** comes into play.

## Instructions
Run the project using `make run` in the root of the repository.
Output is generated in `data/output/function_calls.json`.

To customize the input, you can create your own function definitions and tests
and provide the paths to them when running using `uv run -m src ...`.
When running directly, you can also specify `-i` and `-d` arguments,
which show an inspection of the tokens generated
and dump the model's vocabulary in a text file, respectively.

Example:
```bash
	uv run python -m src \
		--functions_definition data/input/custom_functions_definition.json \
		--input data/input/custom_function_calling_tests.json \
		--output data/output/function_calls.json
```

## Resources
Our interaction with the LLM goes through a wrapper from our school,
creatively named *llm_sdk*.
We are not allowed to use any AI-related packages besides this.
This means a lot of AI-related resources online weren't very relevant.
Also, tutorials on various AI concepts were at a scientific level.
This is why I couldn't find many good resources.
Other students and AI where therefore much more helpful in guiding me.

Nonetheless,
[this tutorial on tokenization](https://huggingface.co/learn/llm-course/chapter6/5)
was helpful to understand the link between characters and tokens.

## Algorithm
Constrained decoding is very similar to deduction.
There are multiple options, and you start off with an empty assumption.
You add "clues" to the assumption and cross out options that aren't valid.
When only one option is valid, you have your result.

In the project, it's implemented as:
1. Append a token to the result.
2. For each option, check up to how far the result matches the option.
3. If the result doesn't match the option at any point, discard the option.
4. If the result runs out of tokens to check,
and the option still matches the result,
the next token from the option is added to a set of valid tokens.

Each option adds one or no tokens to the set. If the set turns out empty,
we're done with the segment of JSON to generate, and move on to the next.
Each segment is represented by a state, managed by a state machine.
A "None" state means the output is finished.

## Design decisions
Besides constrained decoding,
various techniques are used to further improve the results.
- **Autocomplete**: If the constrained decoding yields a single option,
that option is immediately appended without letting the LLM calculate logits.
- **Small context, compact JSON**: The LLM is only fed the function names
and the function descriptions. Spaces are excluded from the JSON output.
This reduces the amount of tokens the LLM needs to consider while reasoning.
- **JSON error guards**: When the LLM is given freedom to generate an argument,
each token is checked to see if it invalidates the JSON format.
If it does, the token is truncated to the part that still follows the format.
- **Data validation**: Let the LLM only generate strings.
Before dumping the results,
all arguments are converted to the correct data types (`"3"` -> `3.0`),
according to the function definitions.

## Performance analysis
For 11 prompts, this program runs slightly longer than a minute.
Each token only takes around 1.5 seconds to generate,
so the bottlenecks are responses with long strings as arguments.

The speed is mostly thanks to the small context.
I considered using *Numpy* in this project, but decided against it.
It'd be a learning experience, but I didn't actually notice any performance
improvements during testing.

Reliability is near 100%: even argument selection is 100% for included tests.

## Challenges faced
