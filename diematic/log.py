import logging

def get_log_level_from(args, config):
    log_level = args.logging
    if 'logging' in config:
        log_level = config['logging']
    return log_level.upper()

def get_logger(level):
    # FIXME: this log format seems ignored...
    FORMAT = ('%(asctime)-15s [%(levelname)-8s] %(module)-15s:%(lineno)-8s %(message)s')
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger()
    logger.setLevel(level)
    return logger