install:
	uv sync --all-groups

run:
	uv run python -m src \
		--functions_definition data/input/functions_definition.json \
		--input data/input/function_calling_tests.json \
		--output data/output/function_calls.json

inspect:
	uv run python -m src \
		--functions_definition data/input/functions_definition.json \
		--input data/input/function_calling_tests.json \
		--output data/output/function_calls.json \
		-i

test_custom:
	uv run python -m src \
		--functions_definition data/input/custom_functions_definition.json \
		--input data/input/custom_function_calling_tests.json \
		--output data/output/function_calls.json

test_regex:
	uv run python -m src \
		--functions_definition data/input/functions_definition.json \
		--input data/input/regex_function_calling_tests.json \
		--output data/output/function_calls.json \
		-i

debug:
	uv run python -m pdb __main__.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint: install
	uv run flake8 --exclude=.venv
	uv run mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--explicit-package-bases \
		--exclude '^(venv|\.venv|env)/'

lint-strict: install
	uv run flake8 --exclude=.venv
	uv run mypy . \
		--strict \
		--explicit-package-bases \
		--exclude '^(venv|\.venv|env)/'

.PHONY: install run debug clean lint lint-strict