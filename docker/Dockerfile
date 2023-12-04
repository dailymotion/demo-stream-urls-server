FROM python:3.11

RUN mkdir /app

WORKDIR /app

RUN pip install pdm

COPY pyproject.toml pdm.lock ./

RUN mkdir /app/src

RUN pdm sync

ENV PATH="/app/.venv/bin:$PATH"

COPY .secrets .secrets

COPY bin bin

COPY src src

CMD ["bin/start-api.sh"]
