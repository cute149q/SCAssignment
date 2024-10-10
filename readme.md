# Timer API
This project is a simple timer API that allows you to to execute scheduled tasks.
For simplicity, let’s assume that tasks can be triggered by accessing a web URL. You create
a task by providing a URL and the desired time to run.
When the specified time arrives, the service will call the URL.

# Installation and Dependencies

## Dependencies
To run this project you need to have pipenv installed. 

Pipenv is a tool that aims to bring the best of all packaging worlds to the Python world. It automatically creates and manages a virtualenv for your projects, as well as adds/removes packages from your Pipfile as you install/uninstall packages. It also generates the ever-important Pipfile.lock, which is used to produce deterministic builds.

If you don't have it installed, you can install it by running the following command:

```bash
pip install pipenv
```

After installing pipenv, you can install the project dependencies by running the following command:

```bash
pipenv install --dev
```

## Running the project

Use the following example vscode configuration files, to enable testing, linting and autoformatting in vscode: `.vscode/settings.json`

```json
{
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": "explicit"
    },
    "files.insertFinalNewline": true,
    "python.testing.pytestArgs": [
        ".",
        "--disable-warnings"
    ],
    "python.testing.pytestEnabled": true,
    "python.testing.autoTestDiscoverOnSaveEnabled": true,
    "python.envFile": "${workspaceFolder}/.env",
    "python.testing.pytestPath": "pytest",
}
```

For debugging locally, a few environment variables need to be set. Create a file named `.env` that assigns
these values. For an up-to-date list of required environment variables, check out `app/models/settings.py`.

```
TIMER_DB_ENDPOINT=cache
TIMER_DB_PORT=6380
ENABLE_DOCS=
TIMER_API_PORT=8000
TIMER_API_HOST=localhost
TIMER_API_URL=http://localhost:8000
TIMER_REDIS_HOST=localhost
TIMER_REDIS_PORT=6380
TIMER_REDIS_URL=http://localhost:6380/0
TIMER_REDIS_SSL_ENABLED=false
```
### Building and running the container image

The whole project can be runned in docker. To build and run the container image, run the following commands:

```bash
./setup_services.sh --build
```
More information about the script can be found in the `setup_services.sh` file. Or you can run the following commands:

```bash
./setup_services.sh --help
```
It can be checked if the service is running healthily by using docker.
```bash
docker ps
```

## Running the tests
In this project we use pytest as the test runner. We have unit tests and integration tests. 

To run the unit tests, you can run the following command:

```bash
./ci.sh
```
The script will check the code style and run the unit tests. A report will be generated (report.xml).

To run the integration tests, the service must be running in docker using the script mentioned in the [[previous section](#building-and-running-the-container-image)]. After that, you can run the following command:

```bash
./run_integration_tests.sh
```

# Functionality

There are two main endpoints in this API:

## Create a task

To create a task, you need to send a POST request to the `/timer` endpoint. The body of the request should be a JSON object with the following fields:

- `url`: The URL that will be called when the task is triggered.
- `hours`: The hour that the task will be triggered.
- `minutes`: The minute that the task will be triggered.
- `seconds`: The second that the task will be triggered.

The `minutes` and `seconds` fields need to be between 0 and 23, 0 and 59 and 0 and 59, respectively.

Example:

```json
{
    "url": "http://example.com",
    "hours": 12,
    "minutes": 30,
    "seconds": 0
}
```
It will return a JSON object with the amount of seconds left until the timer expires
and an id for querying the timer in the future.

Example:

```json
{
    "seconds_left": 3600,
    "id": "123e4567-e89b-12d3-a456-426614174000"
}
```
The endpoint should start an internal timer, which fires a webhook to the
defined URL when the timer expires.

## Get a task

To get a task, you need to send a GET request to the `/timer/{timer_uuid}` endpoint. The `timer_id` parameter is the id of the task you want to get. Returns a JSON object with the amount of seconds left until the timer expires. If the timer already expired, returns 0.

Example:

```json
{
    "time_left": 123,
    "id": "123e4567-e89b-12d3-a456-426614174000"
}
```
