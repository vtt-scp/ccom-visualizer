SHELL=/bin/bash

venv:
	python3.10 -m venv .venv

pip-tools:
	source .venv/bin/activate && \
		pip install --upgrade pip && pip install pip-tools && \
		deactivate

dev-requirements:
	source .venv/bin/activate && \
		cd converter && \
		pip-compile --resolver=backtracking requirements.in && \
		pip-compile --resolver=backtracking dev-requirements.in && \
		pip-sync requirements.txt dev-requirements.txt && \
		deactivate

dev-environment: venv pip-tools dev-requirements

requirements:
	source .venv/bin/activate && \
		cd converter && \
		pip-compile --resolver=backtracking requirements.in && \
		pip-sync requirements.txt && \
		deactivate

build:
	docker compose build

up:
	docker compose up

restart: down up

grafana-install-mqtt:
	docker compose exec -it grafana grafana-cli plugins install grafana-mqtt-datasource

down:
	docker compose down
