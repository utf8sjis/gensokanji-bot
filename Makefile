.PHONY: validate-tweets run format lint test verify

export PYTHONPATH=./src
export ENVFILE_PATH=.env

# tools

validate-tweets:
	PYTHONPATH=$(PYTHONPATH) uv run python scripts/tweet_validator.py

# development

run:
	uv run python src/main.py

format:
	uv run ruff format .

lint:
	uv run ruff format . --check --diff
	uv run ruff check .
	uv run mypy .

test:
	uv run pytest .

verify:
	make format
	make lint
	make test
