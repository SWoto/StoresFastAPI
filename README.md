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

To test, open the container where the api is running, outsite `src` (`/home`) folder and run `pytest --log-cli-level=DEBUG --durations=-0`
 
It is also possible to test functions individually:
```python
pytest src/tests/api/v1/endpoints/test_users.py::TestUser::test_confirm_user --log-cli-level=DEBUG --durations=-0
```

