"""Convert CCOM messages from an MQTT broker to format supported by Grafana."""

import json
import os
import signal
import sys
from typing import Any

from paho.mqtt.client import Client, MQTTMessage

GRAFANA_BROKER = os.environ["GRAFANA_BROKER"]
GRAFANA_BROKER_PORT = int(os.environ["GRAFANA_BROKER_PORT"])
CCOM_BROKER = os.environ["CCOM_BROKER"]
CCOM_BROKER_PORT = int(os.environ["CCOM_BROKER_PORT"])
CCOM_BROKER_USERNAME = os.getenv("CCOM_BROKER_USERNAME")
CCOM_BROKER_PASSWORD = os.getenv("CCOM_BROKER_PASSWORD")


def on_connect(_client: Client, _userdata: Any, _flags: dict, result_code: int) -> None:
    """Notify when connected to a broker."""
    print(f"Connected with result code: {result_code}")


def on_message(_client: Client, grafana_broker: Client, message: MQTTMessage) -> None:
    """
    Convert incoming CCOM messages to format supported by Grafana and
    publish to the MQTT broker Grafana is listening.

    Currently, Grafana MQTT datasource is very limited in supported data formats.
    Only simple key-value pairs are supported.
    """

    data = json.loads(message.payload)
    if not isinstance(data, dict) or "CCOMData" not in data:
        return

    for entity in data["CCOMData"]["entities"]:

        # CCOM message value parsing and format for grafana visualization
        if entity["@@type"] == "SingleDataMeasurement":
            uuid = entity["measurementLocation"]["UUID"]
            name = entity["measurementLocation"].get("name")
            grafana_data_point = {name or uuid: entity["data"]["measure"]["value"]}
        else:
            continue

        grafana_broker.publish(
            f"{message.topic}", json.dumps(grafana_data_point), qos=2
        )


def main() -> None:
    """Main function"""

    grafana_broker = Client(client_id="ccom")
    grafana_broker.on_connect = on_connect
    ccom_broker = Client(client_id="grafana")
    ccom_broker.on_connect = on_connect
    ccom_broker.on_message = on_message
    ccom_broker.user_data_set(grafana_broker)

    print(f"Connecting to Grafana broker at {GRAFANA_BROKER}:{GRAFANA_BROKER_PORT}")
    grafana_broker.connect(GRAFANA_BROKER, port=GRAFANA_BROKER_PORT)

    print(f"Connecting to CCOM broker at {CCOM_BROKER}:{CCOM_BROKER_PORT}")
    if CCOM_BROKER_USERNAME and CCOM_BROKER_PASSWORD:
        ccom_broker.username_pw_set(CCOM_BROKER_USERNAME, CCOM_BROKER_PASSWORD)
    ccom_broker.connect(CCOM_BROKER, port=CCOM_BROKER_PORT)
    ccom_broker.subscribe("ccom/#", qos=2)

    def terminate(_signal, _frame):
        """Stop client loops and terminate program"""
        ccom_broker.loop_stop()
        grafana_broker.loop_stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, terminate)

    try:
        grafana_broker.loop_start()
        ccom_broker.loop_forever()
    except KeyboardInterrupt:
        print("User interrupt")
    finally:
        ccom_broker.loop_stop()
        grafana_broker.loop_stop()


if __name__ == "__main__":
    main()
