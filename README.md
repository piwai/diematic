# diematic

A Python script to monitor De Dietrich boilers equiped with Diematic system, using Modbus RS-845 protocol.
The values fetched from the boiler are sent to an InfluxDB database, for monitoring with tools like [Chronograf](images/chronograf_screenshot.png?raw=true) or [Grafana](images/grafana_screenshot.png?raw=true):

![Screenshot](images/grafana_screenshot.png?raw=true)



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

To create the InfluxDB database, use the [init-file](init-influxdb.sql) file. Be sure to update
the password line 4.

```
influx -database diematic -precision rfc3339.sql < init-influxdb.sql
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
