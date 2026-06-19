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

dump:
	uv run python -m src \
		--functions_definition data/input/functions_definition.json \
		--input data/input/function_calling_tests.json \
		--output data/output/function_calls.json \
		-d

test_custom:
	uv run python -m src \
		--functions_definition data/input/custom_functions_definition.json \
		--input data/input/custom_function_calling_tests.json \
		--output data/output/function_calls.json

debug:
	uv run python -m pdb __main__.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint: install
	uv run flake8 --exclude=.venv,llm_sdk
	uv run mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--explicit-package-bases \
		--exclude '^(venv|\.venv|env|llm_sdk)/'

lint-strict: install
	uv run flake8 --exclude=.venv,llm_sdk
	uv run mypy . \
		--strict \
		--explicit-package-bases \
		--exclude '^(venv|\.venv|env|llm_sdk)/'

.PHONY: install run debug clean lint lint-strict