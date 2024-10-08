#!/usr/bin/env bash

set -euo pipefail


# Reference: https://opensource.com/article/19/12/help-bash-program
Help()
{
   # Display Help
   echo "Perform setup for API integration tests."
   echo
   echo "Syntax: sh setup_service.sh [help|up|build|down]"
   echo "options:"
   echo "help       Print this help."
   echo "up         Bring up the containers."
   echo "build      Builds the docker containers before running."
   echo "down       Brings down and removes the docker containers and network."
   echo
}

GenerateOpenApiJson()
{
    pipenv run python tests/utils/generate_openapi.py
}

export STAGE=dev
export TIMER_API_PORT=8000
export TIMER_API_URL="http://localhost:${TIMER_API_PORT}"
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"
export TIMER_REDIS_PORT=6380
export TIMER_REDIS_URL="http://localhost:${TIMER_REDIS_PORT}"


case  ${1:-} in
    up|build)
    GenerateOpenApiJson
    echo "Bringing up the containers."
    BUILDARG=""
    if [[ ${1:-} = "build" ]]; then
        BUILDARG="--build"
    fi
    docker compose up -d --wait ${BUILDARG}

    echo "Timer API running at: ${TIMER_API_URL}"
    ;;

    down)
    echo "Shutting down all containers."
    docker compose --profile docker_setup down
    ;;

    help)
    Help
    ;;

    *)
    echo "Please provide a valid command."
    Help
    ;;
esac
