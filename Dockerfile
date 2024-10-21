FROM python:3.11-slim
LABEL authors="Matt Kelsey"
COPY ./src /app
COPY ./dicomedit /app/dicomedit
RUN pip install --no-cache-dir -r /app/requirements.txt
ENTRYPOINT ["python", "/app/dicom2inbox.py"]
WORKDIR /app

