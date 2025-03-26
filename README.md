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

### Quick start:

1) Install requirements:
```shell
pip install -r requirements.txt
```

2) Start:
```shell
python src/main.py
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
