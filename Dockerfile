FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

RUN mkdir -p /tado_data_collection
RUN mkdir -p /tado_data_collection/logs

WORKDIR /tado_data_collection

COPY main.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

RUN pip install pandas==2.1.4

CMD ["python", "main.py"]
