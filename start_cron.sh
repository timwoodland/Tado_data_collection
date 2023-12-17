#!/bin/bash
printenv | grep -v "no_proxy" >> /etc/environment
python3 /tado_data_collection/main.py
cron -f