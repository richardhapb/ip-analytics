import datetime
import json
import logging
import os

from flask import Flask
from kafka import KafkaConsumer
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

conn = psycopg2.connect(
    database=os.getenv("POSTGRES_DB"),
    host="127.0.0.1",
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    port=os.getenv("POSTGRES_HOST_PORT"),
)

cur = conn.cursor()

consumer = KafkaConsumer(
    group_id="local-group",
    bootstrap_servers=["127.0.0.1:29092"],
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)


consumer.subscribe(topics=["ip_analytics"])

for msg in consumer:
    logging.info("Info: %s", msg)
