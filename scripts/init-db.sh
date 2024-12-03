#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TABLE ip_analisis (
        ip varchar(15) PRIMARY KEY,
        pais varchar(30),
        reportes_totales integer,
        fecha_ult_reporte datetime,
        estado varchar(15)
    );
    CREATE TABLE comentarios (
        id INTEGER PRIMARY KEY,
        comentario TEXT,
        ip varchar(15) references ip_analisis(ip)
    );
EOSQL



