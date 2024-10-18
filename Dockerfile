FROM python:3.11-slim
LABEL authors="Matt Kelsey"
COPY ./src /app
RUN pip install --no-cache-dir -r /app/requirements.txt
WORKDIR /app

