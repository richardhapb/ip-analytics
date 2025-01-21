"""
Main API module, handle the api requests and kafka messages
"""

import json
import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable, UnrecognizedBrokerVersion

from ip_model import IpData

load_dotenv()
ip_data = IpData()

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_URL")}})

logging.basicConfig(level=logging.INFO)


class KafkaInstance:
    """
    Handle the connection with the Kafka daemon
    """

    def __init__(self):
        self.consumer = None

    def connect_to_kafka(self) -> KafkaConsumer | None:
        """
        Connect to Kafka topic for consume the requests data
        Args:
            No parameters
        Returns:
            Return KafkaConsumer | None: The consumer instance or none if not connected
        """
        if self.consumer is not None:
            return self.consumer
        try:
            self.consumer = KafkaConsumer(
                group_id="local-group",
                bootstrap_servers=["kafka:9092"],
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
                enable_auto_commit=True,
                session_timeout_ms=40000,
            )
            self.consumer.subscribe(topics=["ip_analytics"])
        except (UnrecognizedBrokerVersion, NoBrokersAvailable):
            logging.error("Unrecognized broker version, Kafka is running?")

        return self.consumer


# Connect to Kafka topic
kafka_instance = KafkaInstance()
kafka_instance.connect_to_kafka()


@app.route("/connect_to_kafka")
def connect_kafka():
    """
    Allow to user to conenct manually to Kafka

    Args:
        No parameters
    Returns:
        Return a json with the status message
    """
    kafka_instance.connect_to_kafka()

    if kafka_instance.consumer is None:
        return jsonify({"msg": "Unrecognized broker version, Kafka is running?"}, 400)

    return jsonify({"msg": "Kafka connected"}, 200)


@app.route("/update_ips")
def update_ips():
    """
    Update the requests data from Kafka topic

    Args:
        No parameters.
    Returns:
        Return a json with the status message
    """
    logging.debug("Fetching IPs from DB")
    ip_data.fetch_ips_from_db()

    if kafka_instance.consumer is None:
        logging.debug("Connecting to Kafka")
        kafka_instance.connect_to_kafka()
        if kafka_instance.consumer is None:
            logging.error("Failed to connect to Kafka")
            return jsonify(
                {"msg": "Unrecognized broker version, Kafka is running?"}, 400
            )

    timeout_ms = 4000
    count = 0
    logging.debug("Polling messages from Kafka")
    messages = kafka_instance.consumer.poll(timeout_ms=timeout_ms)
    if messages:
        logging.debug("Messages received from Kafka")
        for _, message_batch in messages.items():
            for msg in message_batch:
                ip = msg.value.get("remote", None)
                timestamp = int(msg.value.get("@timestamp", 0))
                ruta = msg.value.get("path", "")
                if ip:
                    count += 1
                    logging.debug("IP: %s, Timestamp: %s", ip, timestamp)
                    ip_data.insert_ip(ip, timestamp, ruta)

        try:
            logging.debug("Inserting data to DB")
            ip_data.insert_to_db()
        except Exception as e:
            logging.error("Error inserting data to DB: %s", e)
            return jsonify({"msg": "Error inserting data in database"}), 500
    else:
        logging.debug("No messages received from Kafka")

    return jsonify({"data": ip_data.data, "msg": f"{count} ips updated"}), 200


@app.route("/get_data")
def get_data():
    """
    Return the in-memory data

    Args:
        No parameters.
    Returns:
        Return a json with the data
    """
    return jsonify({"data": ip_data.data}), 200


@app.route("/get_ip_data")
def get_ip_data():
    """
    Return only the requested ip data

    Url Params:
        ip: Ip to be requested
    Returns:
        Return dict: A dict with the data
    """
    ip = request.args.get("ip")

    if ip is None:
        return jsonify({"msg": "IP param is required"}), 400

    try:
        data = ip_data.data[ip]
    except KeyError:
        logging.error("The ip doesn't exist")
        return jsonify({"msg": "P doesn't exist"}), 400
    return data


@app.route("/fetch_data_from_db")
def fetch_data_from_db():
    """
    Fetcha data to SQL database and return the result

    Args:
        No parameters.
    Returns:
        Return json with the data or an error message if cannot fetch data
    """
    try:
        ip_data.fetch_ips_from_db()
    except Exception as e:
        logging.error("Error: %s", e)
        return jsonify({"msg": "Error fetching data"}), 400
    return jsonify({"data": ip_data.data}), 200


@app.route("/fetch_requests_from_db")
def fetch_requests_from_db():
    """
    Fetcha requests data to SQL database and return the result

    Args:
        No parameters.
    Returns:
        Return json with the data or an error message if cannot fetch data
    """
    try:
        ip_data.fetch_ips_requests()
    except Exception as e:
        logging.error("Error: %s", e)
        return jsonify({"msg": "Error fetching data"}), 400
    return jsonify({"data": ip_data.solicitudes}), 200


@app.route("/get_ip_requests")
def get_ip_requests():
    """
    Get te requests info from in-memory data or database

    URL Params:
        ip: The direction ip for the request (required)
        from_db: true if require fetch to database
    Returns:
        Return a json with data or an error message if cannot fetch data
    """
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
    app.run("0.0.0.0", 3000, True)

