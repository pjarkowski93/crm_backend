FROM python:3.10-alpine

ARG ENV_NAME

ENV ENV_NAME=${ENV_NAME} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.13

RUN apk update && apk add python3-dev \
                        gcc \
                        libffi-dev \
                        libc-dev \
                        musl-dev \
                        postgresql-dev

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml .flake8 /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$ENV_NAME" == production && echo "--no-dev") --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY crm/ /app/
