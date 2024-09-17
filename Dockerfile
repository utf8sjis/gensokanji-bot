FROM python:3.11-slim-bullseye

WORKDIR /app

ENV PYTHONPATH=./src

COPY pyproject.toml poetry.lock ./
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir poetry && \
    poetry install

COPY src ./src
COPY data ./data

CMD ["poetry", "run", "gunicorn", "-b", "0.0.0.0:8000", "app:app"]
