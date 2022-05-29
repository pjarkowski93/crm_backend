FROM python:3.10-slim-bullseye

ARG ENV_NAME

ENV ENV_NAME=${ENV_NAME} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.13

# RUN apk update && apk add \
#                         python3-dev \
#                         gcc \
#                         libffi-dev \
#                         libc-dev \
#                         musl-dev \
#                         g++ \
#                         postgresql-dev

# RUN wget https://pypi.python.org/packages/da/c6/0936bc5814b429fddb5d6252566fe73a3e40372e6ceaf87de3dec1326f28/pandas-0.22.0-cp36-cp36m-manylinux1_x86_64.whl
# RUN pip install pandas-0.22.0-cp36-cp36m-manylinux1_x86_64.whl

# System deps:
RUN pip install --upgrade pip setuptools
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml .flake8 /app/
ADD crm/ /app/
# ADD templates/ /app/templates/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$ENV_NAME" == production && echo "--no-dev") --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /app
