import logging 
import sys

def get_logger(fp=None):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(threadName)s] [%(levelname)s] >> %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    stream_handler = logging.StreamHandler(
        sys.stdout
    )
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    # Write log msgs into file if filepath is given
    if fp:
        file_handler = logging.FileHandler(
            fp
        )
        logger.addHandler(file_handler)

    return logger