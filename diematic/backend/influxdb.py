import time

from influxdb import InfluxDBClient


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
    influx_client = InfluxDBClient(conf['host'], conf['port'], conf['user'], conf['password'], conf['database'])

    logger.debug(f"Write points: {influx_json_body}")
    influx_client.write_points(influx_json_body, time_precision='ms')