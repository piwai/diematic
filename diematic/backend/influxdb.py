import time

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


def send_data(hostname, data, conf, logger):
    timestamp = int(time.time() * 1000) #milliseconds
    influx_json_body = [
    {
        "measurement": conf['database'],
        "tags": {
            "host": hostname,
        },
        "timestamp": timestamp,
        "fields": data 
    }
    ]
    with InfluxDBClient(url=conf['url'], token=conf['token'], org=conf['org']) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        logger.debug(f"Write points: {influx_json_body}")
        write_api.write(bucket=conf['bucket'],record=influx_json_body)
