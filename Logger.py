import logging
from logging.handlers import RotatingFileHandler

FILE_SIZE = 1024 * 1024 * 100  # 100 MB
BACKUP_COUNT = 5  # keep up to 5 files

class Logger:
    @staticmethod
    def createLogger(debug: bool, version: float):
        if debug:
            level = logging.DEBUG
        else:
            level = logging.WARNING

        fileHandler = RotatingFileHandler(
            "./logs/registerLOL.log",
            mode="a+",
            maxBytes=FILE_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )

        logging.basicConfig(
            format="%(asctime)s %(levelname)s: %(message)s",
            level=level,
            handlers=[fileHandler]
        )
        log = logging.getLogger("register LOL")
        log.info("-------------------------------------------------")
        log.info("-----------------Program started v{version}-------------------------")
        log.info("-------------------------------------------------")
        return log