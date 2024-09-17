.PHONY: validate-tweets format lint test verify docker-build docker-run docker-stop docker-stats docker-clean

export PROJECT_NAME=gensokanji-bot
export IMAGE_NAME=$(PROJECT_NAME)
export CONTAINER_NAME=$(PROJECT_NAME)
export PYTHONPATH=./src

# tools

validate-tweets:
	PYTHONPATH=$(PYTHONPATH) poetry run python scripts/tweet_validator.py

# development

format:
	poetry run isort .
	poetry run black .

lint:
	poetry run pflake8 .
	poetry run mypy .

test:
	poetry run pytest .

verify:
	make format
	make lint
	make test

# docker

docker-build:
	docker buildx build --tag $(IMAGE_NAME) .

docker-run:
	docker run --rm -p 8000:8000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

docker-stop:
	docker stop $(CONTAINER_NAME)

docker-stats:
	docker stats $(CONTAINER_NAME)

docker-clean:
	docker rm $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME)
