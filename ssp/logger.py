import logging

logging.basicConfig(
    format = "%(asctime)s - [%(levelname)s] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s", level=logging.INFO
)

logger = logging.getLogger("logger")

