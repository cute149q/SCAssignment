# syntax=docker/dockerfile:1.3
FROM public.ecr.aws/docker/library/python:3.11-slim-bookworm AS python-deps
RUN pip install --no-cache-dir pipenv
ENV PIPENV_VENV_IN_PROJECT=1
COPY ./Pipfile ./Pipfile.lock ./
RUN pipenv install --deploy

FROM python-deps as test
WORKDIR /code
RUN pipenv install --dev --deploy
COPY ./app /code/app
COPY ./tests /code/app/tests

FROM public.ecr.aws/docker/library/python:3.11-slim-bookworm as runtime
WORKDIR /code
EXPOSE 8000
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
COPY ./app /code/app
