import json
import logging

from flask import Flask, jsonify, request
from kafka import KafkaConsumer
from kafka.errors import UnrecognizedBrokerVersion
from dotenv import load_dotenv

from ip_model import IpData

load_dotenv()

ip_data = IpData()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


class KafkaInstance:
    def __init__(self):
        self.consumer = None

    def connect_to_kafka(self):
        if self.consumer is not None:
            return self.consumer
        try:
            self.consumer = KafkaConsumer(
                group_id="local-group",
                bootstrap_servers=["127.0.0.1:29092"],
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
                enable_auto_commit=True,
            )
            self.consumer.subscribe(topics=["ip_analytics"])
        except UnrecognizedBrokerVersion:
            logging.error("Unrecognized broker version, Kafka is running?")

        return self.consumer


kafka_instance = KafkaInstance()
kafka_instance.connect_to_kafka()


@app.route("/connect_to_kafka")
def connect_kafka():
    kafka_instance.connect_to_kafka()

    if kafka_instance.consumer is None:
        return jsonify({"msg": "Unrecognized broker version, Kafka is running?"}, 400)

    return jsonify({"msg": "Kafka connected"}, 200)


@app.route("/update_ips")
def update_ips():
    if kafka_instance.consumer is None:
        kafka_instance.connect_to_kafka()
        if kafka_instance.consumer is None:
            return jsonify(
                {"msg": "Unrecognized broker version, Kafka is running?"}, 400
            )
    timeout_ms = 5000
    count = 0
    while True:
        messages = kafka_instance.consumer.poll(timeout_ms=timeout_ms)
        if not messages:
            break

        for _, message_batch in messages.items():
            for msg in message_batch:
                ip = msg.value.get("remote", None)
                timestamp = int(msg.value.get("@timestamp", 0))
                ruta = msg.value.get("path", "")
                if ip:
                    count += 1
                    logging.info("IP: %s, Timestamp: %s", ip, timestamp)
                    ip_data.insert_ip(ip, timestamp, ruta)

    try:
        ip_data.insert_to_db()
    except Exception as e:
        logging.error("Error: %s", e)
        return jsonify({"msg": "Error inserting data in database"}), 500

    return jsonify({"msg": f"{count} ips updated"}), 200


@app.route("/get_data")
def get_data():
    return jsonify({"data": ip_data.data}), 200


@app.route("/fetch_data_from_db")
def fetch_data_from_db():
    try:
        ip_data.fetch_ips_from_db()
    except Exception as e:
        logging.error("Error: %s", e)
        return jsonify({"msg": "Error fetching data"}), 400
    return jsonify({"data": ip_data.data}), 200


@app.route("/get_ip_requests")
def get_ip_requests():
    ip = request.args.get("ip")
    from_db = request.args.get("from_db")

    if ip is None:
        logging.error("Error: ip is not in request")
        return jsonify({"msg": "ip argument is necessary"}), 400
    if from_db is not None and from_db.lower() == "true":
        try:
            data = ip_data.fetch_ip_data(ip)
        except Exception as e:
            logging.error("Error: %s", e)
            return jsonify({"msg": "Error fetching data"}), 400
    else:
        try:
            data = ip_data.solicitudes[ip]
        except KeyError:
            return jsonify({"msg": "ip is not in the data"}, 400)
    return jsonify({"data": data}), 200


if __name__ == "__main__":
    app.run("0.0.0.0", 3001, True)
