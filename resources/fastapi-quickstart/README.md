# fastapi-quickstart

This project has the basics to get started running FastAPI locally.
It creates a single FastAPI service.

## Setup
1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)


## Running locally
1. Start the service
```zsh
docker-compose up -d
```

> [!WARNING]
> Verify you see 1 container under `fastapi-quickstart` in Docker desktop.

## Using curl

1. Open a shell
```zsh
curl -X GET http://127.0.0.1:8001/info | jq
```
