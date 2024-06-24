.PHONY: format lint verify-all

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
