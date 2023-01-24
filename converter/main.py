import json
import random
import signal
import sys
import time
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from paho.mqtt.client import Client

MEASUREMENT_LOCATION_ID = "7026830e-e0e4-45eb-bf1b-09eff4a612a3"
CCOM_BROKER = "localhost"
CCOM_BROKER_PORT = 1884
GRAFANA_BROKER = "localhost"
GRAFANA_BROKER_PORT = 1883
GENERATOR = True

ccom_broker = Client(client_id="generator")
grafana_broker = Client(client_id="ccom")


def utc_rfc3339_to_datetime(date: str) -> datetime:
    """Convert UTC RFC 3339 datetime string to Python datetime object"""

    return datetime.fromisoformat(date.replace("Z", "")).replace(tzinfo=ZoneInfo("UTC"))


def on_connect(client, userdata, flags, rc) -> None:
    print("Connected with result code " + str(rc))


def on_message(client: Client, userdata, message) -> None:
    ccom_data = json.loads(message.payload).get("CCOMData")
    grafana_data = [
        {
            "value": entity["data"]["measure"]["value"],
            "timestamp": entity["recorded"]["dateTime"],
        }
        for entity in ccom_data["entities"]
        if entity["@@type"] == "SingleDataMeasurement"
    ]
    for data_point in grafana_data:
        grafana_broker.publish(f"ccom/{message.topic}", json.dumps(data_point), qos=2)


def publish_generated_ccom_message(client: Client) -> None:
    ccom_message = {
        "CCOMData": {
            "@ccomVersion": "4.1.0-draft",
            "entities": [
                {
                    "@@type": "SingleDataMeasurement",
                    "UUID": str(uuid.uuid4()),
                    "measurementLocation": {"UUID": MEASUREMENT_LOCATION_ID},
                    "recorded": {
                        "@format": "RFC 3339",
                        "dateTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    },
                    "data": {
                        "measure": {"value": round(random.uniform(60, 80), 0)},
                    },
                }
            ],
        }
    }
    client.publish(
        f"{MEASUREMENT_LOCATION_ID}", payload=json.dumps(ccom_message), qos=2
    )


if __name__ == "__main__":

    # mqtt.username_pw_set("generator", os.getenv("GEN_PW", "whabbajack"))
    ccom_broker.on_connect = on_connect
    grafana_broker.on_connect = on_connect
    ccom_broker.on_message = on_message
    ccom_broker.connect(CCOM_BROKER, port=CCOM_BROKER_PORT)
    grafana_broker.connect(GRAFANA_BROKER, port=GRAFANA_BROKER_PORT)
    ccom_broker.subscribe("#", qos=2)

    grafana_broker.loop_start()

    try:
        if GENERATOR:
            ccom_broker.loop_start()
            while True:
                publish_generated_ccom_message(ccom_broker)
                time.sleep(3)
        else:
            ccom_broker.loop_forever()
    except KeyboardInterrupt:
        print("User interrupt")
    finally:
        ccom_broker.loop_stop()
