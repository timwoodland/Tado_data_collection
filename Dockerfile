FROM ubuntu:22.04

COPY main.py /tado_data_collection/
COPY requirements.txt /tado_data_collection/
COPY crontab /tado_data_collection/
COPY start_cron.sh /tado_data_collection/

#Install cron, python and pip
RUN apt-get update \
    && apt-get install -y cron \
    && apt-get install -y python3 \
    && apt-get install -y pip

RUN pip install -r /tado_data_collection/requirements.txt

RUN pip install pandas==2.1.4

RUN crontab /tado_data_collection/crontab

RUN ["chmod", "+x", "/tado_data_collection/start_cron.sh"]

CMD ["/tado_data_collection/start_cron.sh"]
