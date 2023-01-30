SHELL=/bin/bash

pip-tools:
	pip install --upgrade pip pip-tools wheel

requirements: pip-tools
	pip-compile --generate-hashes --resolver backtracking -o converter/requirements/app.txt converter/pyproject.toml
	pip-compile --generate-hashes --extra dev --resolver backtracking -o converter/requirements/dev.txt converter/pyproject.toml

sync-requirements:
	pip-sync converter/requirements/dev.txt converter/requirements/app.txt

build:
	docker compose build

debug:
	docker compose up

up:
	docker compose up -d

down:
	docker compose down

restart: down up

grafana-install-mqtt:
	docker compose exec -it grafana grafana-cli plugins install grafana-mqtt-datasource
