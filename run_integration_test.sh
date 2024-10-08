export PYTHONPATH=$(pwd)

pipenv run python -m pytest -v tests/integration --disable-warnings
