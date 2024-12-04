
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

RUN apt update &\
    pip install --upgrade pip & \
    pip install -r requirements.txt

COPY . /app

EXPOSE 3000
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:3000", "main:app", "-k", "gevent")

