import os
import logging
from functools import wraps

import requests
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection

from config import DATABASE_CONFIG

load_dotenv()

API_URL = os.getenv("ABUSEIPDB_CHECK_URL", "")
API_KEY = os.getenv("ABUSEIPDB_API_KEY")


def db_connection(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.db_conn is None or self.db_conn.closed:
            self.db_conn = psycopg2.connect(**DATABASE_CONFIG)
            self.db_conn.set_client_encoding("UTF8")

        try:
            result = None
            if self.db_conn is not None:
                result = func(self, *args, **kwargs)
        except psycopg2.Error as e:
            self.db_conn.rollback()
            logging.error("Error executign database query")
            raise psycopg2.Error(e)
        else:
            self.db_conn.commit()
            return result
        finally:
            self.db_conn.close()
            self.db_conn = None

    return wrapper


class IpData:
    IP_ANALISIS_STRUCTURE = [
        "ip",
        "pais",
        "reportes_totales",
        "fecha_ult_reporte",
        "dominio",
        "estado",
    ]
    SOLICITUDES_STRUCTURE = ["timestamp_sol", "ip", "ruta"]

    def __init__(self):
        self.db_conn: connection | None = None
        self.solicitudes: dict[str, list] = {}
        self.data: dict[str, dict] = {}

    def get_data(self) -> dict[str, dict]:
        return self.data

    def insert_ip(self, ip: str, timestamp: int, ruta: str) -> None:
        if ip not in self.data:
            self.data[ip] = {}
            self.request_ip_info(ip)

        if ip not in self.solicitudes:
            self.solicitudes[ip] = []

        self.solicitudes[ip].append((timestamp, ruta))

    def request_ip_info(self, ip: str):
        if not API_URL:
            return

        ESTADOS = ["Confiable", "Sospechosa", "Maliciosa"]

        params = {"ipAddress": ip, "maxAgeInDays": 90, "verbose": None}
        headers = {"Key": API_KEY, "Accept": "application/json"}

        try:
            response = requests.get(API_URL, headers=headers, params=params, timeout=10)
            data = response.json().get("data")
            self.data[ip]["pais"] = data.get("countryCode")
            self.data[ip]["dominio"] = data.get("domain")
            self.data[ip]["fecha_ult_reporte"] = data.get("lastReportedAt")
            total_reports = data.get("totalReports")
            self.data[ip]["reportes_totales"] = total_reports

            estado = total_reports // 5

            self.data[ip]["estado"] = ESTADOS[min(estado, 2)]
        except requests.ConnectionError as e:
            logging.error("Error: %s\n Error in request to api for ip %s", e, ip)
        except (ValueError, KeyError) as e:
            logging.error("Error inserting data to the model: %s", e)

    @db_connection
    def insert_to_db(self):
        if not self.data:
            logging.warning("The ips list is empty, cannot insert in database")
            return

        ip_elements = [
            (k, *v.values())
            for k, v in self.data.items()
            if len(v.values()) == len(IpData.IP_ANALISIS_STRUCTURE) - 1
        ]

        cols = ["ip"] + [v for v in next(iter(self.data.values()))]

        query_ips = (
            "INSERT INTO ip_analytics.ip_analisis ("
            + ",".join(cols)
            + ") VALUES ("
            + ",".join(["%s"] * len(IpData.IP_ANALISIS_STRUCTURE))
            + ") ON CONFLICT ("
            + IpData.IP_ANALISIS_STRUCTURE[0]
            + ") DO UPDATE SET "
            + ", ".join([col + "=EXCLUDED." + col for col in cols if col != "ip"])
        )

        assert self.db_conn is not None, "Database connection is empty"

        cur = self.db_conn.cursor()

        cur.executemany(query_ips, ip_elements)

        if self.solicitudes:

            solicitudes_elements = [
                (t[0], k, t[1]) for k, v in self.solicitudes.items() for t in v
            ]

            query_solicitudes = (
                "INSERT INTO ip_analytics.solicitudes ("
                + ",".join(IpData.SOLICITUDES_STRUCTURE)
                + ") VALUES ("
                + ",".join(["%s"] * len(IpData.SOLICITUDES_STRUCTURE))
                + ") ON CONFLICT ("
                + IpData.SOLICITUDES_STRUCTURE[0]
                + ", "
                + IpData.SOLICITUDES_STRUCTURE[1]
                + ") DO NOTHING"
            )

            cur.executemany(query_solicitudes, solicitudes_elements)

        cur.close()

    @db_connection
    def fetch_ips_from_db(self) -> dict[str, dict]:
        query = (
            "SELECT "
            + ",".join(IpData.IP_ANALISIS_STRUCTURE)
            + " FROM ip_analytics.ip_analisis"
        )
        assert self.db_conn is not None, "Database connection is empty"

        cur = self.db_conn.cursor()

        cur.execute(query)

        ips_elements = cur.fetchall()

        for element in ips_elements:
            self.data[element[0]] = dict(
                zip(IpData.IP_ANALISIS_STRUCTURE[1:], element[1:])
            )

        cur.close()

        return self.data

    @db_connection
    def fetch_ip_data(self, ip: str) -> list:
        query = (
            "SELECT "
            + ", ".join(IpData.SOLICITUDES_STRUCTURE)
            + " FROM ip_analytics.solicitudes"
            + " WHERE ip = '"
            + ip
            + "'"
        )

        assert self.db_conn is not None, "Database connection is empty"

        cur = self.db_conn.cursor()

        cur.execute(query)

        sol_elements = cur.fetchall()

        self.solicitudes[ip] = []

        for element in sol_elements:
            self.solicitudes[ip].append((element[0], element[2]))
        cur.close()

        return self.solicitudes[ip]
