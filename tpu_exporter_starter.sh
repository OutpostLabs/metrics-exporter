#!/bin/bash

source venv/bin/activate
sudo chmod -R 777 /opt/tpu_exporter
sudo chmod -R 777 /opt/tpu_exporter/venv
/opt/tpu_exporter/venv/bin/pip install  prometheus_client google-cloud-monitoring
/opt/tpu_exporter/venv/bin/python /opt/tpu_exporter/tpu_exporter.py --variable "$1"
