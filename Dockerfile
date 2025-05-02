FROM python:3.11-slim-bullseye

WORKDIR /app

ENV PYTHONPATH=./src

COPY pyproject.toml uv.lock ./
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir uv && \
    uv sync

COPY src ./src
COPY resources ./resources

CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:8000", "wsgi:app"]
