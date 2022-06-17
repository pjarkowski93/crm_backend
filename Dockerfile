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

RUN apt-get update
RUN apt-get -y install wkhtmltopdf


# System deps:
RUN pip install --upgrade pip setuptools
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml .flake8 Procfile heroku.yml /app/
ADD app/ /app/
# ADD templates/ /app/templates/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$ENV_NAME" == production && echo "--no-dev") --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /app

CMD [ "gunicorn -b 0.0.0.0:80 wsgi" ]
