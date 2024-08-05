import os
import errno
import logging


class LoggingHandler(logging.Logger):
    def __init__(
        self,
        name: str,
        folderpath: str,
        level: str = "NOTSET",
        format: str = "%(asctime).19s | %(levelname).4s | %(message)s",
        filemode: str = "a+",
    ):
        super().__init__(name=name, level=level)
        self.name = name
        folderpath = os.path.normpath(folderpath)
        self.folderpath = folderpath
        if not name.lower().endswith(".log"):
            name += ".log"
        self.filename = name
        self.filepath = os.path.normpath(os.path.join(folderpath, name))
        self.filemode = filemode
        self.format = format
        self.strLevel = level
        self.init()

    def __del__(self):
        pass

    def init(self):
        try:
            os.makedirs(self.folderpath)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            pass
        file_handler = logging.FileHandler(filename=self.filepath, mode=self.filemode)
        formatter = logging.Formatter(self.format)
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)
        self.critical(f"**********************")
        self.critical(f"** Starting...")
        self.critical(f"** Log Level: {self.strLevel}")

    def get_level_number(self, level: str = None):
        name_to_level = {
            "CRITICAL": 50,
            "FATAL": 50,
            "ERROR": 40,
            "WARN": 30,
            "WARNING": 30,
            "INFO": 20,
            "DEBUG": 10,
            "NOTSET": 0,
        }
        if level is None:
            level = self.level
        level = level.upper()
        if level in name_to_level.keys():
            level_number = name_to_level[level]
        else:
            level_number = name_to_level["NOTSET"]
        return level_number

    def close(self):
        self.critical(f"** Closing log file...")
        self.critical(f"**********************")
        if self.hasHandlers():
            self.handlers[0].close()
