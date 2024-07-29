FROM python:3.9

COPY main.py /tado_data_collection/
COPY requirements.txt /tado_data_collection/

RUN pip install -r /tado_data_collection/requirements.txt

RUN pip install pandas==2.1.4

CMD ["python", "./tado_data_collection/main.py"]
