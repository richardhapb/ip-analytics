#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS ${POSTGRES_SCHEMA};
    CREATE TABLE IF NOT EXISTS ${POSTGRES_SCHEMA}.ip_analisis (
        ip varchar(15) PRIMARY KEY,
        pais varchar(30),
        reportes_totales integer,
        fecha_ult_reporte timestamp,  
        estado varchar(15)
    );
    CREATE TABLE IF NOT EXISTS ${POSTGRES_SCHEMA}.comentarios (
        id SERIAL PRIMARY KEY,
        comentario TEXT,
        ip varchar(15) REFERENCES ${POSTGRES_SCHEMA}.ip_analisis(ip)
    );
EOSQL
