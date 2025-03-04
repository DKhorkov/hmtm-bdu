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
# TODO переделать на питон
2) Run application:
```shell
go run ./cmd/server/server.go
```

## Linters

To run linters, use next command:
```shell
task -d scripts linters -v
```

## Tests

To run test, use next commands.Coverage docs will be
recorded to ```coverage``` folder:
```shell
task -d scripts tests -v
```
