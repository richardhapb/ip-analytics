FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc \
        libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv && pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 3000
CMD ["gunicorn", "main:app", "--workers", "2", "--bind", "0.0.0.0:3000", "-k", "gevent", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "debug"]

