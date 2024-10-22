FROM python:3.11-slim
LABEL authors="Matt Kelsey"
COPY ./src /app
COPY ./dicomedit /app/dicomedit
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN apt-get update && apt-get install -y default-jdk
ENTRYPOINT ["python", "/app/dicom2inbox.py"]
WORKDIR /app

