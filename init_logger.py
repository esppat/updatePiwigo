import logging


def add_file_handler(logfile_name, level, module_name=''):
    logger = logging.getLogger(module_name)
    fh = logging.FileHandler(logfile_name)
    fh.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def add_console_handler(level, module_name=''):
    logger = logging.getLogger(module_name)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)    


def init_logger(logfile_name, module_name='', console_level=logging.DEBUG, file_level=logging.DEBUG):
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    add_file_handler(logfile_name=logfile_name, level=file_level)
    add_console_handler(level=console_level, module_name=module_name)
