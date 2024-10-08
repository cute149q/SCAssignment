#!/usr/bin/env bash

set -exo pipefail

pipenv verify

pipenv run black --line-length 120 --check "app" "tests" 
pipenv run isort --check --profile=black --project=app "./app" "./tests" 
pipenv run mypy --ignore-missing-imports "app" 
pipenv run pylint --fail-under=9 --rcfile=".pylintrc" "app"
pipenv run python -m pytest tests/unit -vv --disable-warnings --junitxml=report.xml ${DEFAULT_PYTEST_ARGS}
