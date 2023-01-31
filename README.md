# CCOM-Visualizer <!-- omit in toc -->
Visualize CCOM data from an MQTT broker with Grafana.

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Quickstart](#quickstart)
  - [Install MQTT datasource in Grafana](#install-mqtt-datasource-in-grafana)
- [Development](#development)
  - [Environment](#environment)
  - [Making changes](#making-changes)

# Prerequisites
- Docker
- Docker compose
- Python `>=3.10` (for development)
- Linux based system

# Setup
Set the required settings to a `.env` file at project root.
```
CCOM_BROKER_IP = 127.0.0.1
CCOM_BROKER_PORT = 1883
CCOM_BROKER_USERNAME = user
CCOM_BROKER_PASSWORD = pass
```

# Quickstart
Build the converter image; start Grafana, MQTT broker, and CCOM converter containers; and install Grafana MQTT data source plugin with command:
```
make
```
Grafana can now be locally accessed at [`http://localhost:3000`](http://localhost:3000)  
Grafana related files are stored in a (persitent) docker volume called `grafana-storage`.

## Install MQTT datasource in Grafana
1. Login, and navigate `Configuration` > `Data sources` 
2. Click `Add data source`
3. Search for `MQTT` and select the `MQTT` data source
4. Set name for the datasource, for example `CCOM`
5. Set `Connection`: `URI` as `tcp://grafana-broker:1883`
6. Click `Save & test`
7. You can now use the `CCOM` data source in dash boards panels, etc.

# Development
Check the [makefile](makefile) to see what each `make` target does.

## Environment
For developing the converter script, create a development environment with: 
```
make dev-env
```
Activate the created Python virtual environment with:
```
source .venv/bin/activate
```

## Making changes
Write changes to Python requirements in [pyproject.toml](converter/pyproject.toml).

Update the requirements files under `converter/requirements/` with:
```
make requirements
```
Synchronise requirement changes to current virtual environment:
```
make dev-env
```
Rebuild the converter script docker image:
```
docker compose build
```
Restart the containers
```
docker compose down
docker compose up -d
```
