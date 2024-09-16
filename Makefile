.PHONY: format lint test verify-all validate-tweets

format:
	poetry run isort .
	poetry run black .

lint:
	poetry run pflake8 .
	poetry run mypy .

test:
	poetry run pytest .

verify-all:
	make format
	make lint
	make test

validate-tweets:
	PYTHONPATH="src" poetry run python scripts/tweet_validator.py
