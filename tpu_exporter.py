
import time
from google.cloud import monitoring_v3
from prometheus_client import start_http_server, Gauge
import argparse

global project_id
global accelerator_utilization
global client
global project_name
global tpu_utilization

def main():
    global project_id
    global accelerator_utilization
    global client
    global project_name
    global tpu_utilization

    parser = argparse.ArgumentParser(description="Fetch the project_id value.")
    
    parser.add_argument('--variable', type=str, required=True, help="The value for the project_id variable")
    
    args = parser.parse_args()
    
    project_id = args.variable

    accelerator_utilization = Gauge('accelerator_utilization', 'TPU Accelerator Utilization Percentage')
    tpu_utilization = Gauge('tpu_utilization', 'TPU Utilization Percentage')


    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

def fetch_utilization(metric_type, prometheus_metric):
    """
    Fetches utilization metrics from Google Cloud Monitoring and updates Prometheus metric., multiplying the value with 100 to make it as a percentage

    Args:
        metric_type (str): The GCP metric type to query (e.g., CPU or GPU utilization).
        prometheus_metric (Gauge): The corresponding Prometheus metric to update.
    """
    interval = monitoring_v3.TimeInterval({
        "end_time": {"seconds": int(time.time())},
        "start_time": {"seconds": int(time.time()) - 600}, 
    })

    try:
        results = client.list_time_series(
            request={
                "name": project_name,
                "filter": f'metric.type = "{metric_type}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )

        for result in results:
            for point in result.points:
                utilization = point.value.double_value * 100 
                prometheus_metric.set(utilization)

    except Exception as e:
        print(f"Error fetching {metric_type}: {e}")


if __name__ == "__main__":
    main()
    start_http_server(9102)  
    while True:
        
        fetch_utilization("tpu.googleapis.com/tpu/mxu/utilization", tpu_utilization)

        fetch_utilization("tpu.googleapis.com/accelerator/tensorcore_utilization", accelerator_utilization)

        time.sleep(20)