install:
	uv sync --all-groups

run:
	uv run python -m src \
		--functions_definition data/input/functions_definition.json \
		--input data/input/function_calling_tests.json \
		--output data/output/function_calls.json

custom:
	uv run python -m src \
		-f data/input/custom_functions_definition.json \
		-i data/input/custom_function_calling_tests.json \
		-o data/output/custom_function_calls.json \
		-m HuggingFaceTB/SmolLM2-1.7B \
		-t 60

debug:
	uv run python -m pdb -m src

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