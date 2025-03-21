## Usage

Before usage need to create network for correct dependencies work:
```shell
task -d scripts network -v
```

### Run via docker:

To run app and it's dependencies in docker, use next command:
```shell
task -d scripts prod -v
```

### Run via source files:

To run application via source files, use next commands:
1) Run all application dependencies:
```shell
task -d scripts local -v
```
# To-do:
2) Run application:
```shell
go run ./cmd/server/server.go
```

## Linters

To run linters, use next command:
```shell
flake8 ./
```

## Typiziter
```shell
mypy ./
```

## Tests

```shell
pytest -v
```
