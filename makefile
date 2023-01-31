SHELL=/bin/bash
PYTHON_VERSION=3.10
VENV_PATH=.venv

all: build up grafana-install-mqtt

venv:
	@test -d $(VENV_PATH) && echo "Virtualenv '$(VENV_PATH)' found." || \
	echo "Virtualenv not found. Creating a virtualenv using: 'python$(PYTHON_VERSION) -m venv $(VENV_PATH)'" && \
	python$(PYTHON_VERSION) -m venv $(VENV_PATH)

pip-tools: venv
	source $(VENV_PATH)/bin/activate && \
	pip install --upgrade pip pip-tools wheel

dev-env: pip-tools
	source $(VENV_PATH)/bin/activate && \
		pip-sync converter/requirements/dev.txt converter/requirements/app.txt

requirements: pip-tools
	source $(VENV_PATH)/bin/activate && \
		pip-compile --generate-hashes --resolver backtracking -o converter/requirements/app.txt converter/pyproject.toml && \
	pip-compile --generate-hashes --extra dev --resolver backtracking -o converter/requirements/dev.txt converter/pyproject.toml

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
	docker compose stop grafana
	docker compose up grafana -d
