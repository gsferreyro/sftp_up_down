import os
import errno
import configparser


class ConfigHandler(configparser.ConfigParser):
    def __init__(self, name: str, folderpath: str):
        super().__init__(os.environ)
        if not name.lower().endswith(".ini"):
            name += ".ini"
        self.name = name
        folderpath = os.path.normpath(folderpath)
        self.folderpath = folderpath
        self.filepath = os.path.normpath(os.path.join(folderpath, name))
        self._load_config()

    def _load_config(self):
        if not os.path.exists(self.filepath):
            self._create_config()
            self._init_config()
        self.read(self.filepath)

    def _init_config(self):
        filename = os.path.splitext(self.name)[0]
        config = configparser.RawConfigParser()
        config.read(self.filepath)

        homepath = os.path.normpath(os.environ["homepath"])
        homedrive = os.path.normpath(os.environ["homedrive"])
        bufferfolder = os.path.normpath(
            f"{homepath}{os.path.normpath('/buffer')}{os.path.normpath('/')}"
        )
        logfolder = os.path.normpath(
            f"{homepath}{os.path.normpath('/logs')}{os.path.normpath('/')}"
        )

        if config.has_option("Buffer", "bufferdisk"):
            config.set("Buffer", "bufferdisk", f"{homedrive}")
        if config.has_option("Buffer", "bufferrootfolder"):
            config.set(
                "Buffer", "bufferrootfolder", f"{bufferfolder}{os.path.normpath('/')}"
            )
        if config.has_option("Buffer", "buffername"):
            config.set("Buffer", "buffername", f"{filename}")

        if config.has_option("Logs", "logdisk"):
            config.set("Logs", "logdisk", f"{homedrive}")
        if config.has_option("Logs", "logrootfolder"):
            config.set("Logs", "logrootfolder", f"{logfolder}{os.path.normpath('/')}")
        if config.has_option("Logs", "logname"):
            config.set("Logs", "logname", f"{filename}")
        if config.has_option("Logs", "loglevel"):
            config.set("Logs", "loglevel", "ERROR")

        with open(self.filepath, "w") as configfile:
            config.write(configfile)

    def _create_config(self):
        config = configparser.RawConfigParser()
        config_dict = {
            "Parametros": {"live_run": "False", "mail_test": "", "mail_live": ""},
            "Buffer": {
                "bufferdisk": "",
                "bufferrootfolder": "",
                "buffername": "",
                "bufferpath": "%(bufferdisk)s%(bufferrootfolder)s%(buffername)s",
            },
            "Logs": {
                "logdisk": "",
                "logrootfolder": "",
                "logname": "",
                "logpath": "%(logdisk)s%(logrootfolder)s%(logname)s",
                "loglevel": "ERROR",
            },
            "SMTP": {"server": "", "port": "", "user": "", "pass": ""},
        }
        config.read_dict(config_dict)

        try:
            os.makedirs(self.folderpath)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            pass
        with open(self.filepath, "w") as configfile:
            config.write(configfile)

    def get(
        self,
        section,
        option,
        *,
        raw=False,
        exit_if_not_exist: bool = True,
        val_type: str = "str",
        dict_separator: str = ",",
        **kwargs,
    ):
        valid_val_types = {"str", "bool", "int", "dict"}
        if val_type not in val_type:
            raise ValueError(
                "get_config: val_type must be one of %r." % valid_val_types
            )

        if val_type == "dict":
            return self.getdict(
                section=section, option=option, exit_if_not_exist=exit_if_not_exist
            )
        try:
            if val_type == "str":
                return super().get(section=section, option=option, raw=raw, **kwargs)
            elif val_type == "bool":
                return super().getboolean(section=section, option=option, raw=raw)
            elif val_type == "int":
                return super().getint(section=section, option=option, raw=raw)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            print(f"Error: {e}")
            if exit_if_not_exist:
                exit(1)
            return None

    def getdict(
        self, section, option, dict_separator: str = ",", exit_if_not_exist: bool = True
    ):
        value = self.get(
            section=section, option=option, exit_if_not_exist=exit_if_not_exist
        )
        if value:
            value = value.replace("  ", " ").replace(", ", ",").replace(" ,", ",")
            dict = value.split(dict_separator)
        else:
            dict = []
        return dict
