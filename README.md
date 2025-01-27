# diematic

A Python script to monitor De Dietrich boilers equiped with Diematic system, using Modbus RS-845 protocol.
The values fetched from the boiler are sent to an InfluxDB database, for monitoring with tools like [Chronograf](images/chronograf_screenshot.png?raw=true).

NOTE: The [original repository](https://github.com/gmasse/diematic/) isn't maintained any more, but I will continue to update this fork.

## Hardware requirements

 * A De Dietrich boiler with Diematic regulation and a mini-din socket
 * A mini-din cable 
 * A RS-845 to USB adapter
 * A nano-computer with a USB port and Python3 installed (Raspberry pi or similar)

Check links in the "references" section below on how to do the hardware setup.

## Installation
```
git clone https://github.com/gmasse/diematic.git
cd diematic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp diematic.yaml.orig diematic.yaml
vi diematic.yaml
```

## Test
Run `python3 diematic.py --help`
```
usage: diematic.py [-h] [-b {none,influxdb}] [-d DEVICE]
                   [-l {critical,error,warning,info,debug}]

optional arguments:
  -h, --help            show this help message and exit
  -b {none,influxdb}, --backend {none,influxdb}
                        select data backend (default is influxdb)
  -d DEVICE, --device DEVICE
                        define modbus device
  -l {critical,error,warning,info,debug}, --logging {critical,error,warning,info,debug}
                        define logging level (default is critical)
```
`python3 diematic.py --backend none --logging debug`

## InfluxDB preparation
### Minimal
```
CREATE DATABASE "diematic"
CREATE USER "diematic" WITH PASSWORD 'mySecurePas$w0rd'
GRANT ALL ON "diematic" TO "diematic"
CREATE RETENTION POLICY "one_week" ON "diematic" DURATION 1w REPLICATION 1 DEFAULT
```

### Additionnal steps for down-sampling
```
CREATE RETENTION POLICY "five_weeks" ON "diematic" DURATION 5w REPLICATION 1
CREATE RETENTION POLICY "five_years" ON "diematic" DURATION 260w REPLICATION 1

CREATE CONTINUOUS QUERY "cq_month" ON "diematic" BEGIN
  SELECT mean(/temperature/) AS "mean_1h", mean(/pressure/) AS "mean_1h", max(/temperature/) AS "max_1h", max(/pressure/) AS "max_1h"
  INTO "five_weeks".:MEASUREMENT
  FROM "one_week"."diematic"
  GROUP BY time(1h),*
END

CREATE CONTINUOUS QUERY "cq_year" ON "diematic" BEGIN
  SELECT mean(/^mean_.*temperature/) AS "mean_24h", mean(/^mean_.*pressure/) AS "mean_24h", max(/^max_.*temperature/) AS "max_24h", max(/^max_.*pressure/) AS "max_24h"
  INTO "five_years".:MEASUREMENT
  FROM "five_weeks"."diematic"
  GROUP BY time(24h),*
END
```


## Crontab
To run the script every minute and feed the database, `crontab -e` and add the following line:
```
*/1 *   * * *       ~/diematic/launcher.sh
```


## References
- [Modbus protocol](https://github.com/riptideio/pymodbus)
- [A thread on De Dietrich diematic in a french forum](https://www.domotique-fibaro.fr/topic/5677-de-dietrich-diematic-isystem/)
- [Modbus registers sheet](https://drive.google.com/file/d/156qBsfRGJvOpJBJu5K4WMHUuwv34bZQN/view?usp=sharing)
