import yaml
import os.path
import argparse
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

from diematic import log
from diematic.boiler import Boiler
from diematic.backend import influxdb


DEFAULT_MODBUS_RETRIES = 3
DEFAULT_MODBUS_TIMEOUT = 10
DEFAULT_MODBUS_BAUDRATE = 9600
DEFAULT_MODBUS_UNIT = 10
DEFAULT_MODBUS_DEVICE = None

# --------------------------------------------------------------------------- #
# retrieve command line arguments
# --------------------------------------------------------------------------- #
parser = argparse.ArgumentParser()
parser.add_argument("-b", "--backend", choices=['none', 'influxdb'], default='influxdb', help="select data backend (default is influxdb)")
parser.add_argument("-d", "--device", help="define modbus device")
parser.add_argument("-l", "--logging", choices=['critical', 'error', 'warning', 'info', 'debug'], default='info', help="define logging level (default is info)")
args = parser.parse_args()

# --------------------------------------------------------------------------- #
# retrieve config from diematic.yaml
# --------------------------------------------------------------------------- #
main_base = os.path.dirname(__file__)
config_file = os.path.join(main_base, "..", "diematic.yaml")
if not os.path.exists(config_file):
    raise FileNotFoundError(f"Configuration file {config_file} not found")
with open(config_file) as f:
    # use safe_load instead load
    cfg = yaml.safe_load(f)

# Set logger
loglevel = log.get_log_level_from(args, cfg)
logger = log.get_logger(loglevel)

# --------------------------------------------------------------------------- #
# set configuration variables (command line prevails on configuration file)
# --------------------------------------------------------------------------- #
MODBUS_RETRIES = None
MODBUS_TIMEOUT = None
MODBUS_BAUDRATE = None
MODBUS_UNIT = None
MODBUS_DEVICE = None

if 'modbus' in cfg:
    if isinstance(cfg['modbus']['retries'], int):
        MODBUS_RETRIES = cfg['modbus']['retries']
    if isinstance(cfg['modbus']['timeout'], int):
        MODBUS_TIMEOUT = cfg['modbus']['timeout']
    if isinstance(cfg['modbus']['baudrate'], int):
        MODBUS_BAUDRATE = cfg['modbus']['baudrate']
    if isinstance(cfg['modbus']['unit'], int):
        MODBUS_UNIT = cfg['modbus']['unit']
    if isinstance(cfg['modbus']['device'], str):
        MODBUS_DEVICE = cfg['modbus']['device']

if args.device:
    MODBUS_DEVICE = args.device


# --------------------------------------------------------------------------- #
# check mandatory configuration variables
# --------------------------------------------------------------------------- #
if MODBUS_DEVICE is None:
    raise ValueError('Modbus device not set')

# --------------------------------------------------------------------------- #
# check optional configuration variables
# --------------------------------------------------------------------------- #
if MODBUS_RETRIES is None:
    MODBUS_RETRIES = DEFAULT_MODBUS_RETRIES
if MODBUS_TIMEOUT is None:
    MODBUS_TIMEOUT = DEFAULT_MODBUS_TIMEOUT
if MODBUS_BAUDRATE is None:
    MODBUS_BAUDRATE = DEFAULT_MODBUS_BAUDRATE
if MODBUS_UNIT is None:
    MODBUS_UNIT = DEFAULT_MODBUS_UNIT



# --------------------------------------------------------------------------- #
# let's go!
# --------------------------------------------------------------------------- #
MyBoiler = Boiler(index=cfg['registers'], logger=log)

def run_sync_client():
    #enabling modbus communication
    client = ModbusClient(method='rtu', port=MODBUS_DEVICE, timeout=MODBUS_TIMEOUT, baudrate=MODBUS_BAUDRATE)
    client.connect()

    MyBoiler.registers = []
    id_stop = -1

    for mbrange in cfg['modbus']['register_ranges']:
        id_start = mbrange[0]
        MyBoiler.registers.extend([None] * (id_start-id_stop-1))
        id_stop = mbrange[1]

        for i in range(MODBUS_RETRIES):
            logger.debug(f"Attempt {i} to read registers from {id_start} to {id_stop}")
            rr = client.read_holding_registers(count=(id_stop-id_start+1), address=id_start, unit=MODBUS_UNIT)
            if rr.isError():
                logger.error(rr.message)
                MyBoiler.registers.extend([None] * (id_stop-id_start+1))
            else:
                MyBoiler.registers.extend(rr.registers)
                break
    client.close()

    #parsing registers to push data in Object attributes
    MyBoiler.browse_registers()
    logger.info("Dumping values\n" + MyBoiler.dump())


    #pushing data to influxdb
    if args.backend == 'influxdb':
        influxdb.send_data('raspberrypi', MyBoiler.fetch_data(), cfg['influxdb'], logger)


if __name__ == "__main__":
    run_sync_client()
