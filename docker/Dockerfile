FROM python:3.11 AS requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN apt-get update
RUN apt-get install libpq-dev -y

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/
COPY ./alembic.ini /code/
COPY ./alembic /code/alembic/
COPY ./certs /code/certs/

CMD ["python", "main.py"]
