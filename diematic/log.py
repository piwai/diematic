import logging


def get_logger(args, config):
    FORMAT = ('%(asctime)-15s [%(levelname)-8s] %(module)-15s:%(lineno)-8s %(message)s')
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger()
    log_level = args.logging
    if 'logging' in config:
        log_level = config['logging']
    numeric_level = getattr(logging, log_level.upper())
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    logger.setLevel(numeric_level)
    return logger