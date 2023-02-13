FROM python:3.10-slim

WORKDIR /usr/src/app

RUN mkdir -p /storage/ivac/suspects

COPY requirements.txt ./

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./


CMD [ "python", "-u", "app.py" ]
