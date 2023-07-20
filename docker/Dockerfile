FROM python:3.11.1-slim

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade poetry

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app

COPY ./poetry.lock ./pyproject.toml /app/

COPY ./roller_bot /app/roller_bot/
COPY ./assets /app/assets/

RUN poetry install --no-interaction --no-ansi --no-cache

ENTRYPOINT ["poetry", "run"]
CMD ["poetry", "run", "bot"]
