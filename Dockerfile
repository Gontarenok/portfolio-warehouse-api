FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry==1.8.4

COPY pyproject.toml poetry.lock* README.md ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

RUN poetry install --no-interaction --no-ansi

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
