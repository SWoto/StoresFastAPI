# StoresFastAPI
An API for simulated stores built using FastAPI and AWS

## How to
It uses docker to run containers, to run the api, just use the command:
```
docker compose up
```
or 
```
docker compose up --build
```
to force building the containers.

To test, open the container where the api is running, outsite `src` folder and run `pytest --log-cli-level=DEBUG`